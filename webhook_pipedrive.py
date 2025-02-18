import json  # ← Adicionar esta linha no topo
import requests
import os
import time
from flask import Flask, request, jsonify
import logging
from dotenv import load_dotenv

# Configuração avançada de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
load_dotenv()

# Constantes
ACEITE_VERBAL_ID = int(os.getenv('ACEITE_VERBAL_ID', 4))
ASSINATURA_CONTRATO_ID = int(os.getenv('ASSINATURA_CONTRATO_ID', 5))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
COMPANY_DOMAIN = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')
MAX_RETRIES = 3  # Número de tentativas para buscar dados atualizados

# Validação rigorosa das variáveis de ambiente
required_vars = {
    'ACEITE_VERBAL_ID': ACEITE_VERBAL_ID,
    'ASSINATURA_CONTRATO_ID': ASSINATURA_CONTRATO_ID,
    'WEBHOOK_URL': WEBHOOK_URL,
    'PIPEDRIVE_API_TOKEN': API_TOKEN,
    'PIPEDRIVE_COMPANY_DOMAIN': COMPANY_DOMAIN
}

missing_vars = [var for var, val in required_vars.items() if not val]
if missing_vars:
    logging.error(f'Variáveis de ambiente faltando: {", ".join(missing_vars)}')
    exit(1)

app = Flask(__name__)

def get_deal_with_retry(deal_id):
    """Busca dados do deal com retentativa e verificação de consistência"""
    for attempt in range(MAX_RETRIES):
        try:
            url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/deals/{deal_id}'
            params = {
                'api_token': API_TOKEN,
                'include_product_data': 1  # Garante todos os campos relacionados
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('success', True):
                logging.error(f'Resposta não bem-sucedida: {result.get("error")}')
                continue
                
            if not result.get('data'):
                logging.error(f'Dados do deal {deal_id} não encontrados (tentativa {attempt+1})')
                continue
                
            # Verificação de campos críticos
            required_fields = ['id', 'stage_id', 'stage_change_time']
            if not all(field in result['data'] for field in required_fields):
                logging.error(f'Campos essenciais faltando (tentativa {attempt+1})')
                continue
                
            logging.info(f'Dados do deal {deal_id} obtidos com sucesso na tentativa {attempt+1}')
            return result['data']
            
        except requests.exceptions.RequestException as e:
            logging.error(f'Erro na tentativa {attempt+1}: {str(e)}')
            time.sleep(2 ** attempt)  # Backoff exponencial
            
    return None

def validate_deal_structure(deal_data):
    """Valida a estrutura completa dos dados do deal"""
    try:
        # Verificação de estrutura hierárquica
        if not isinstance(deal_data.get('creator_user_id'), dict):
            logging.error('Estrutura creator_user_id inválida')
            return False
            
        if not isinstance(deal_data.get('person_id'), dict):
            logging.error('Estrutura person_id inválida')
            return False
            
        # Verificação de campos numéricos
        if not isinstance(deal_data.get('value'), (int, float)):
            logging.error('Tipo inválido para value')
            return False
            
        # Verificação de timestamps
        timestamp_fields = ['add_time', 'update_time', 'stage_change_time']
        for field in timestamp_fields:
            if field in deal_data and not isinstance(deal_data[field], str):
                logging.error(f'Formato inválido para {field}')
                return False
                
        return True
        
    except Exception as e:
        logging.error(f'Erro na validação: {str(e)}')
        return False

@app.route('/pipedrive-webhook', methods=['POST'])
def handle_pipedrive_webhook():
    """Endpoint principal para processamento de webhooks"""
    try:
        logging.info('-' * 50)
        logging.info('Nova requisição recebida')
        
        # Decodificação segura dos dados
        try:
            data = request.get_json(force=True, silent=True)
            if not data:
                logging.error('Payload JSON inválido ou vazio')
                return jsonify({'error': 'Invalid JSON'}), 400
        except Exception as e:
            logging.error(f'Erro ao decodificar JSON: {str(e)}')
            return jsonify({'error': 'Invalid JSON format'}), 400

        logging.debug(f'Payload recebido: {json.dumps(data, indent=2)}')  # ← Aqui usamos json.dumps
        
        # Validação estrutural do payload
        required_keys = ['current', 'previous', 'event']
        if not all(key in data for key in required_keys):
            logging.error('Estrutura do payload inválida')
            return jsonify({'error': 'Invalid payload structure'}), 400

        current = data['current']
        previous = data['previous']
        deal_id = current.get('id')
        
        if not deal_id:
            logging.error('ID do deal não encontrado')
            return jsonify({'error': 'Missing deal ID'}), 400

        # Verificação da transição de estágio
        if not (previous.get('stage_id') == ACEITE_VERBAL_ID and 
                current.get('stage_id') == ASSINATURA_CONTRATO_ID):
            logging.info('Mudança de estágio não relevante. Ignorando.')
            return jsonify({'status': 'ignored'}), 200

        logging.info(f'Processando deal {deal_id} - Transição de estágio detectada')
        
        # Obtenção dos dados completos com retentativa
        deal_data = get_deal_with_retry(deal_id)
        if not deal_data:
            logging.error('Falha ao obter dados atualizados do deal')
            return jsonify({'error': 'Failed to fetch deal data'}), 500
            
        # Validação completa da estrutura
        if not validate_deal_structure(deal_data):
            logging.error('Dados do deal não passaram na validação')
            return jsonify({'error': 'Invalid deal structure'}), 500

        logging.debug(f'Dados completos do deal: {json.dumps(deal_data, indent=2)}')
        
        # Envio para webhook externo
        try:
            start_time = time.time()
            response = requests.post(
                WEBHOOK_URL,
                json=deal_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Pipedrive-Webhook-Integration/1.0'
                },
                timeout=15
            )
            duration = time.time() - start_time
                
            logging.info(f'Resposta do webhook: {response.status_code} (Tempo: {duration:.2f}s)')
            
            if not response.ok:
                logging.error(f'Erro no webhook: {response.text}')
                return jsonify({'error': 'Webhook delivery failed'}), 500
                
            logging.info('Dados enviados com sucesso')
            return jsonify({'status': 'success'}), 200
            
        except requests.exceptions.RequestException as e:
            logging.error(f'Falha na conexão com webhook: {str(e)}')
            return jsonify({'error': 'Webhook connection failed'}), 500
            
    except Exception as e:
        logging.error(f'Erro não tratado: {str(e)}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)