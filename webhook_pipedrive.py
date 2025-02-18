import requests
import json
import os
from flask import Flask, request, jsonify
import logging
from pipedrive.client import Client
from dotenv import load_dotenv

# Configuração inicial
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
load_dotenv()

# Constantes
ACEITE_VERBAL_ID = int(os.getenv('ACEITE_VERBAL_ID', 4))
ASSINATURA_CONTRATO_ID = int(os.getenv('ASSINATURA_CONTRATO_ID', 5))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
COMPANY_DOMAIN = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')

# Validação das variáveis de ambiente
required_vars = {
    'ACEITE_VERBAL_ID': ACEITE_VERBAL_ID,
    'ASSINATURA_CONTRATO_ID': ASSINATURA_CONTRATO_ID,
    'WEBHOOK_URL': WEBHOOK_URL,
    'PIPEDRIVE_API_TOKEN': API_TOKEN,
    'PIPEDRIVE_COMPANY_DOMAIN': COMPANY_DOMAIN
}

missing_vars = [var for var, val in required_vars.items() if not val]
if missing_vars:
    logging.error(f'Variáveis faltando: {", ".join(missing_vars)}')
    exit(1)

# Inicialização do cliente Pipedrive (CORRIGIDO)
try:
    client = Client(company_domain=COMPANY_DOMAIN)  # Parâmetro corrigido
    client.set_api_token(API_TOKEN)
except Exception as e:
    logging.error(f"Erro na inicialização do cliente Pipedrive: {str(e)}")
    exit(1)

app = Flask(__name__)

def fetch_deal_details(deal_id):
    """Obtém detalhes completos do deal formatados"""
    try:
        # Busca o deal usando a API diretamente para maior controle
        url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/deals/{deal_id}'
        params = {'api_token': API_TOKEN}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        deal = response.json()
        if not deal.get('data'):
            logging.error(f'Deal {deal_id} não encontrado')
            return None

        deal_data = deal['data']
        
        # Estruturação dos dados (mantido seu formato original)
        user_data = {
            'id': deal_data['creator_user_id']['id'],
            'name': deal_data['creator_user_id']['name'],
            'email': deal_data['creator_user_id']['email'],
            'value': deal_data['creator_user_id']['id']
        }

        return {
            'id': deal_data['id'],
            'stage_id': deal_data['stage_id'],
            'creator_user_id': user_data,
            'user_id': user_data,
            'person_id': {
                'name': deal_data['person_name'],
                'email': deal_data['person_id']['email'][0]['value'] if deal_data['person_id']['email'] else None,
                'phone': deal_data['person_id']['phone'][0]['value'] if deal_data['person_id']['phone'] else None
            },
            'org_id': {
                'name': deal_data['org_name'],
                'address': deal_data['org_id']['address']
            },
            'title': deal_data['title'],
            'value': deal_data['value'],
            'currency': deal_data['currency'],
            'stage_change_time': deal_data['stage_change_time'],
            'status': deal_data['status'],
            'webhook_data': deal_data
        }

    except Exception as e:
        logging.error(f'Erro ao buscar deal {deal_id}: {str(e)}')
        return None

@app.route('/pipedrive-webhook', methods=['POST'])
def handle_pipedrive_webhook():
    """Endpoint para receber webhooks do Pipedrive"""
    try:
        data = request.json
        logging.info('Evento recebido do Pipedrive')
        
        # Verificação reforçada da estrutura
        required_keys = ['current', 'previous', 'event']
        if not all(key in data for key in required_keys):
            logging.warning(f'Formato inválido. Chaves esperadas: {required_keys}')
            return jsonify({'status': 'invalid format'}), 400

        current = data['current']
        previous = data['previous']
        
        # Extrair estágios com fallback seguro
        previous_stage = previous.get('stage_id')
        current_stage = current.get('stage_id')
        deal_id = current.get('id')

        if not all([previous_stage, current_stage, deal_id]):
            logging.warning('Dados incompletos para processamento')
            return jsonify({'status': 'incomplete data'}), 400

        # Verificar transição específica
        if (int(previous_stage) == ACEITE_VERBAL_ID and 
            int(current_stage) == ASSINATURA_CONTRATO_ID):
            
            logging.info(f'Mudança válida detectada: Deal {deal_id}')
            
            deal_details = fetch_deal_details(deal_id)
            if not deal_details:
                return jsonify({'status': 'deal not found'}), 404

            try:
                response = requests.post(
                    WEBHOOK_URL,
                    json=deal_details,
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                )
                
                if response.ok:
                    logging.info(f'Webhook externo respondido com sucesso')
                    return jsonify({
                        'status': 'success',
                        'webhook_response': response.text
                    }), 200
                
                logging.error(f'Erro no webhook: {response.status_code}')
                return jsonify({
                    'status': 'webhook_error',
                    'status_code': response.status_code,
                    'response': response.text
                }), 502

            except requests.exceptions.RequestException as e:
                logging.error(f'Falha de conexão: {str(e)}')
                return jsonify({'status': 'connection failed'}), 503

        return jsonify({'status': 'no action required'}), 200

    except Exception as e:
        logging.error(f'Erro crítico: {str(e)}', exc_info=True)
        return jsonify({'status': 'server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)