from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging

# Configurar logging
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
    """Busca dados completos do deal"""
    url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/deals/{deal_id}'
    params = {'api_token': API_TOKEN}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('data'):
            return result['data']
        logging.error(f"Erro na API: {result.get('error', 'Sem dados')}")
        return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição: {str(e)}")
        return None

def get_person_details(person_id):
    """Busca detalhes completos da pessoa"""
    url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/persons/{person_id}'
    params = {'api_token': API_TOKEN}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('data'):
            return result['data']
        logging.error(f"Erro na API de pessoas: {result.get('error', 'Sem dados')}")
        return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição de pessoa: {str(e)}")
        return None

def get_organization_details(org_id):
    """Busca detalhes completos da organização"""
    url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/organizations/{org_id}'
    params = {'api_token': API_TOKEN}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('data'):
            return result['data']
        logging.error(f"Erro na API de organizações: {result.get('error', 'Sem dados')}")
        return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição de organização: {str(e)}")
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
                
                # Busca dados completos do deal
                full_deal = get_full_deal_data(deal_id)
                
                if full_deal:
                    # Busca detalhes da pessoa associada ao deal
                    person_details = get_person_details(full_deal.get('person_id', {}).get('value'))
                    
                    # Busca detalhes da organização associada ao deal
                    org_details = get_organization_details(full_deal.get('org_id', {}).get('value'))
                    
                    # Combina todos os dados
                    combined_data = {
                        "original_webhook_data": data,
                        "full_deal_data": full_deal,
                        "person_details": person_details,
                        "organization_details": org_details
                    }
                    
                    try:
                        # Envia payload combinado
                        response = requests.post(
                            WEBHOOK_URL,
                            json=combined_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=10
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