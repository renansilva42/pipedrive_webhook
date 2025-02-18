import requests
import os
from flask import Flask, request, jsonify
import logging
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

app = Flask(__name__)

def fetch_deal_details(deal_id):
    """Obtém detalhes completos do deal usando a API REST"""
    try:
        url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/deals/{deal_id}'
        params = {'api_token': API_TOKEN}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        if not result.get('data'):
            logging.error(f'Deal {deal_id} não encontrado')
            return None

        deal_data = result['data']
        
        # Estruturação dos dados
        return {
            'id': deal_data['id'],
            'stage_id': deal_data['stage_id'],
            'title': deal_data['title'],
            'value': deal_data['value'],
            'currency': deal_data['currency'],
            'person_name': deal_data.get('person_name'),
            'org_name': deal_data.get('org_name'),
            'stage_change_time': deal_data.get('stage_change_time'),
            'raw_data': deal_data  # Todos os dados originais
        }

    except requests.exceptions.RequestException as e:
        logging.error(f'Erro na API: {str(e)}')
        return None
    except Exception as e:
        logging.error(f'Erro geral: {str(e)}')
        return None

@app.route('/pipedrive-webhook', methods=['POST'])
def handle_pipedrive_webhook():
    """Endpoint para webhook do Pipedrive"""
    try:
        data = request.json
        logging.info('Evento recebido')
        
        # Validação básica
        if not all(key in data for key in ['current', 'previous']):
            return jsonify({'error': 'Formato inválido'}), 400

        current = data['current']
        previous = data['previous']
        deal_id = current.get('id')
        
        # Verificar transição de estágio
        if (previous.get('stage_id') == ACEITE_VERBAL_ID and
            current.get('stage_id') == ASSINATURA_CONTRATO_ID):
            
            logging.info(f'Processando deal {deal_id}')
            
            deal_details = fetch_deal_details(deal_id)
            if not deal_details:
                return jsonify({'error': 'Deal não encontrado'}), 404

            # Envio para webhook externo
            try:
                response = requests.post(
                    WEBHOOK_URL,
                    json=deal_details,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                response.raise_for_status()
                logging.info('Dados enviados com sucesso')
                return jsonify({'status': 'success'}), 200
                
            except requests.exceptions.RequestException as e:
                logging.error(f'Erro no webhook: {str(e)}')
                return jsonify({'error': 'Falha no envio'}), 500

        return jsonify({'status': 'ignorado'}), 200

    except Exception as e:
        logging.error(f'Erro crítico: {str(e)}')
        return jsonify({'error': 'Erro interno'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)