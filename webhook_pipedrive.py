from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging
import json
from get_details_of_deal import get_deal_details  # Importando a função de get_deal_details.py

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


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    logging.info(f"Dados recebidos: {data}")

    if 'current' in data and 'previous' in data:
        current_stage_id = data['current'].get('stage_id')
        previous_stage_id = data['previous'].get('stage_id')

        # Detecta mudança de estágio de 4 para 5
        if previous_stage_id == ACEITE_VERBAL_ID and current_stage_id == ASSINATURA_CONTRATO_ID:
            deal_id = data['current'].get('id')
            if deal_id:
                logging.info(f"Detectada mudança de estágio para assinatura no Deal {deal_id}")

                # Busca os dados completos do deal usando a biblioteca do Pipedrive
                full_deal = get_deal_details(deal_id)

                if full_deal:
                    # Combina os dados originais com os dados completos
                    combined_data = {
                        "original_webhook_data": data,
                        "full_deal_data": full_deal
                    }

                    logging.info(f"Payload combinado: {json.dumps(combined_data, indent=4)}")

                    # Envia o payload para o webhook externo
                    try:
                        response = requests.post(
                            WEBHOOK_URL,
                            json=combined_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=5
                        )

                        # Verifica se a requisição foi bem-sucedida
                        if response.status_code == 200:
                            logging.info(f"Dados completos do Deal {deal_id} enviados com sucesso!")
                        else:
                            logging.error(f"Erro ao enviar para o webhook: {response.status_code} - {response.text}")

                    except requests.exceptions.RequestException as e:
                        logging.error(f"Falha ao enviar para o webhook: {str(e)}")
                else:
                    logging.error(f"Falha ao obter dados completos do Deal {deal_id}")
            else:
                logging.error("ID do deal não encontrado nos dados recebidos")
    else:
        logging.warning("Estrutura de dados recebida não corresponde ao esperado")

    return jsonify({"status": "received"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
