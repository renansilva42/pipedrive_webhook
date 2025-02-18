from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging
import json

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente
load_dotenv()

# Imprimir variáveis de ambiente para debug
logging.info(f"ACEITE_VERBAL_ID: {os.getenv('ACEITE_VERBAL_ID')}")
logging.info(f"ASSINATURA_CONTRATO_ID: {os.getenv('ASSINATURA_CONTRATO_ID')}")
logging.info(f"WEBHOOK_URL: {os.getenv('WEBHOOK_URL')}")
logging.info(f"PIPEDRIVE_API_TOKEN: {os.getenv('PIPEDRIVE_API_TOKEN')}")
logging.info(f"PIPEDRIVE_COMPANY_DOMAIN: {os.getenv('PIPEDRIVE_COMPANY_DOMAIN')}")

app = Flask(__name__)

# Configurações
ACEITE_VERBAL_ID = os.getenv('ACEITE_VERBAL_ID')
ASSINATURA_CONTRATO_ID = os.getenv('ASSINATURA_CONTRATO_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
COMPANY_DOMAIN = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')

# Verificação das variáveis de ambiente
if not all([ACEITE_VERBAL_ID, ASSINATURA_CONTRATO_ID, WEBHOOK_URL, API_TOKEN, COMPANY_DOMAIN]):
    missing_vars = [var for var in ['ACEITE_VERBAL_ID', 'ASSINATURA_CONTRATO_ID', 'WEBHOOK_URL', 'PIPEDRIVE_API_TOKEN', 'PIPEDRIVE_COMPANY_DOMAIN'] if not os.getenv(var)]
    raise ValueError(f"As seguintes variáveis de ambiente não estão definidas: {', '.join(missing_vars)}")

try:
    ACEITE_VERBAL_ID = int(ACEITE_VERBAL_ID)
    ASSINATURA_CONTRATO_ID = int(ASSINATURA_CONTRATO_ID)
except ValueError:
    raise ValueError("ACEITE_VERBAL_ID e ASSINATURA_CONTRATO_ID devem ser números inteiros válidos.")

def get_full_deal_data(deal_id):
    """Busca dados completos do deal, incluindo informações sobre a pessoa e a organização"""
    url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/deals/{deal_id}'
    params = {'api_token': API_TOKEN}
    
    try:
        logging.info(f"Buscando dados do deal com ID: {deal_id}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('data'):
            deal_data = result['data']
            logging.info(f"Dados do deal: {deal_data}")

            # Buscar dados sobre a pessoa
            if 'person_id' in deal_data:
                person_url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/persons/{deal_data["person_id"]}'
                logging.info(f"Buscando dados da pessoa com ID: {deal_data['person_id']}")
                person_response = requests.get(person_url, params=params)
                person_data = person_response.json().get('data', {})
                logging.info(f"Dados da pessoa: {person_data}")
            else:
                person_data = {}

            # Buscar dados sobre a organização
            if 'org_id' in deal_data:
                org_url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/organizations/{deal_data["org_id"]}'
                logging.info(f"Buscando dados da organização com ID: {deal_data['org_id']}")
                org_response = requests.get(org_url, params=params)
                org_data = org_response.json().get('data', {})
                logging.info(f"Dados da organização: {org_data}")
            else:
                org_data = {}

            # Buscar dados sobre o criador do deal (usuário)
            if 'creator_user_id' in deal_data:
                user_url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/users/{deal_data["creator_user_id"]}'
                logging.info(f"Buscando dados do criador do deal com ID: {deal_data['creator_user_id']}")
                user_response = requests.get(user_url, params=params)
                user_data = user_response.json().get('data', {})
                logging.info(f"Dados do criador do deal: {user_data}")
            else:
                user_data = {}
            
            # Combina os dados
            full_data = {
                "deal": deal_data,
                "person": person_data,
                "organization": org_data,
                "creator_user": user_data
            }
            
            return full_data
        else:
            logging.error("Erro ao buscar dados do deal: Dados não encontrados")
            return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição: {str(e)}")
        return None

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    logging.info(f"Dados recebidos: {data}")
    
    if 'current' in data and 'previous' in data:
        current_stage_id = data['current'].get('stage_id')
        previous_stage_id = data['previous'].get('stage_id')

        if previous_stage_id == ACEITE_VERBAL_ID and current_stage_id == ASSINATURA_CONTRATO_ID:
            deal_id = data['current'].get('id')
            if deal_id:
                logging.info(f"Detectada mudança para assinatura no Deal {deal_id}")
                
                # Busca dados completos
                full_deal = get_full_deal_data(deal_id)
                
                if full_deal:
                    # Combina os dados originais com os dados completos
                    combined_data = {
                        "original_webhook_data": data,
                        "full_deal_data": full_deal
                    }
                    logging.info(f"Payload combinado: {json.dumps(combined_data, indent=4)}")
                    
                    try:
                        # Envia payload combinado
                        response = requests.post(
                            WEBHOOK_URL,
                            json=combined_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            logging.info(f"Dados completos do Deal {deal_id} enviados com sucesso!")
                        else:
                            logging.error(f"Erro no destino: {response.status_code} - {response.text}")
                            
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Falha no envio: {str(e)}")
                else:
                    logging.error(f"Falha ao obter dados do Deal {deal_id}")
            else:
                logging.error("ID do deal não encontrado nos dados recebidos")
    else:
        logging.warning("Estrutura de dados recebida não corresponde ao esperado")

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=5000)
