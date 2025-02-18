from pipedrive.client import Client
import os
import json
import requests
from flask import Flask, request, jsonify
import logging
from dotenv import load_dotenv

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log das variáveis de ambiente carregadas (sem expor valores sensíveis)
logging.info("Verificando variáveis de ambiente carregadas:")
logging.info(f"ACEITE_VERBAL_ID está definido: {bool(os.getenv('ACEITE_VERBAL_ID'))}")
logging.info(f"ASSINATURA_CONTRATO_ID está definido: {bool(os.getenv('ASSINATURA_CONTRATO_ID'))}")
logging.info(f"WEBHOOK_URL está definido: {bool(os.getenv('WEBHOOK_URL'))}")
logging.info(f"PIPEDRIVE_API_TOKEN está definido: {bool(os.getenv('PIPEDRIVE_API_TOKEN'))}")
logging.info(f"PIPEDRIVE_COMPANY_DOMAIN está definido: {bool(os.getenv('PIPEDRIVE_COMPANY_DOMAIN'))}")

# Carregar variáveis de ambiente
load_dotenv()

def get_deal_details(deal_id):
    """
    Busca os detalhes do deal no formato específico requerido.
    """
    try:
        # Inicializando o cliente do Pipedrive
        client = Client(domain=os.getenv('PIPEDRIVE_COMPANY_DOMAIN'))
        client.set_api_token(os.getenv('PIPEDRIVE_API_TOKEN'))

        logging.info(f"Buscando detalhes do deal {deal_id}...")

        # Obtendo o deal com todos os dados relacionados
        deal = client.deals.get_deal(deal_id)
        if not deal:
            logging.error(f"Deal {deal_id} não encontrado")
            return None

        # Obtendo dados do criador do deal
        creator = client.users.get_user(deal['creator_user_id'])
        
        # Obtendo dados do proprietário do deal
        owner = client.users.get_user(deal['user_id'])
        
        # Obtendo dados da pessoa
        person = client.persons.get_person(deal['person_id'])
        
        # Obtendo dados da organização
        org = client.organizations.get_organization(deal['org_id'])

        # Estruturando os dados do usuário (creator e owner)
        user_data = {
            "id": creator['id'],
            "name": creator['name'],
            "email": creator['email'],
            "has_pic": creator['has_pic'],
            "pic_hash": creator['pic_hash'],
            "active_flag": creator['active_flag'],
            "value": creator['id']
        }

        # Estruturando os dados da pessoa
        person_data = {
            "active_flag": person['active_flag'],
            "name": person['name'],
            "email": person['email'],
            "phone": person['phone'],
            "owner_id": person['owner_id'],
            "company_id": person['company_id'],
            "value": person['id']
        }

        # Estruturando os dados da organização
        org_data = {
            "name": org['name'],
            "people_count": org['people_count'],
            "owner_id": org['owner_id'],
            "address": org['address'],
            "label_ids": org['label_ids'],
            "active_flag": org['active_flag'],
            "cc_email": org['cc_email'],
            "owner_name": owner['name'],
            "value": org['id']
        }

        # Estruturando o deal completo no formato especificado
        formatted_deal = {
            "id": deal['id'],
            "creator_user_id": user_data,
            "user_id": user_data,  # Mesmo dados do creator neste caso
            "person_id": person_data,
            "org_id": org_data,
            "stage_id": deal['stage_id'],
            "title": deal['title'],
            "value": deal['value'],
            "currency": deal['currency'],
            "add_time": deal['add_time'],
            "update_time": deal['update_time'],
            "stage_change_time": deal['stage_change_time'],
            "active": deal['active'],
            "deleted": deal['deleted'],
            "status": deal['status'],
            "probability": deal['probability'],
            "next_activity_date": deal['next_activity_date'],
            "next_activity_time": deal['next_activity_time'],
            "next_activity_id": deal['next_activity_id'],
            "last_activity_id": deal['last_activity_id'],
            "last_activity_date": deal['last_activity_date'],
            "lost_reason": deal['lost_reason'],
            "visible_to": deal['visible_to'],
            "close_time": deal['close_time'],
            "pipeline_id": deal['pipeline_id'],
            "won_time": deal['won_time'],
            "first_won_time": deal['first_won_time'],
            "lost_time": deal['lost_time'],
            "products_count": deal['products_count'],
            "files_count": deal['files_count'],
            "notes_count": deal['notes_count'],
            "followers_count": deal['followers_count'],
            "email_messages_count": deal['email_messages_count'],
            "activities_count": deal['activities_count'],
            "done_activities_count": deal['done_activities_count'],
            "undone_activities_count": deal['undone_activities_count'],
            "participants_count": deal['participants_count'],
            "expected_close_date": deal['expected_close_date'],
            "last_incoming_mail_time": deal['last_incoming_mail_time'],
            "last_outgoing_mail_time": deal['last_outgoing_mail_time'],
            "label": deal['label'],
            "stage_order_nr": deal['stage_order_nr'],
            "person_name": deal['person_name'],
            "org_name": deal['org_name'],
            "next_activity_subject": deal['next_activity_subject'],
            "next_activity_type": deal['next_activity_type'],
            "next_activity_duration": deal['next_activity_duration'],
            "next_activity_note": deal['next_activity_note'],
            "formatted_value": deal['formatted_value'],
            "weighted_value": deal['weighted_value'],
            "formatted_weighted_value": deal['formatted_weighted_value'],
            "weighted_value_currency": deal['weighted_value_currency'],
            "rotten_time": deal['rotten_time'],
            "owner_name": deal['owner_name'],
            "cc_email": deal['cc_email'],
            "org_hidden": deal['org_hidden'],
            "person_hidden": deal['person_hidden'],
            "average_time_to_won": deal['average_time_to_won'],
            "average_stage_progress": deal['average_stage_progress'],
            "age": deal['age'],
            "stay_in_pipeline_stages": deal['stay_in_pipeline_stages'],
            "last_activity": deal['last_activity'],
            "next_activity": deal['next_activity']
        }

        return formatted_deal

    except Exception as err:
        logging.error(f"Erro ao obter detalhes do deal: {str(err)}")
        return None

# Carregar variáveis de ambiente manualmente
ACEITE_VERBAL_ID = int(os.getenv('ACEITE_VERBAL_ID'))
ASSINATURA_CONTRATO_ID = int(os.getenv('ASSINATURA_CONTRATO_ID'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PIPEDRIVE_API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
PIPEDRIVE_COMPANY_DOMAIN = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')

# Verificar se todas as variáveis foram carregadas
if not all([ACEITE_VERBAL_ID, ASSINATURA_CONTRATO_ID, WEBHOOK_URL, PIPEDRIVE_API_TOKEN, PIPEDRIVE_COMPANY_DOMAIN]):
    logging.error("Algumas variáveis de ambiente não foram carregadas corretamente:")
    if not ACEITE_VERBAL_ID:
        logging.error("ACEITE_VERBAL_ID não está definido")
    if not ASSINATURA_CONTRATO_ID:
        logging.error("ASSINATURA_CONTRATO_ID não está definido")
    if not WEBHOOK_URL:
        logging.error("WEBHOOK_URL não está definido")
    if not PIPEDRIVE_API_TOKEN:
        logging.error("PIPEDRIVE_API_TOKEN não está definido")
    if not PIPEDRIVE_COMPANY_DOMAIN:
        logging.error("PIPEDRIVE_COMPANY_DOMAIN não está definido")
    raise ValueError("Variáveis de ambiente necessárias não estão definidas")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        data = request.json
        logging.info("Webhook recebido do Pipedrive")
        
        if not all(k in data for k in ['current', 'previous']):
            logging.warning("Dados recebidos não contêm as chaves esperadas")
            return jsonify({"status": "invalid_data"}), 400

        current_stage_id = data['current'].get('stage_id')
        previous_stage_id = data['previous'].get('stage_id')
        
        # Verifica a mudança específica de estágio
        if (previous_stage_id == ACEITE_VERBAL_ID and 
            current_stage_id == ASSINATURA_CONTRATO_ID):
            
            deal_id = data['current'].get('id')
            if not deal_id:
                logging.error("ID do deal não encontrado nos dados")
                return jsonify({"status": "missing_deal_id"}), 400

            logging.info(f"Processando mudança de estágio para deal {deal_id}")
            
            # Obtém dados completos do deal
            deal_data = get_deal_details(deal_id)
            if not deal_data:
                logging.error(f"Falha ao obter dados completos do deal {deal_id}")
                return jsonify({"status": "deal_fetch_failed"}), 500

            # Envia para o webhook externo
            try:
                response = requests.post(
                    WEBHOOK_URL,
                    json=deal_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    logging.info(f"Dados enviados com sucesso para webhook externo")
                    return jsonify({"status": "success"}), 200
                else:
                    logging.error(f"Erro ao enviar para webhook: {response.status_code}")
                    return jsonify({"status": "webhook_failed"}), 500

            except requests.exceptions.RequestException as e:
                logging.error(f"Exceção ao enviar para webhook: {str(e)}")
                return jsonify({"status": "webhook_error"}), 500

        return jsonify({"status": "no_action_required"}), 200

    except Exception as e:
        logging.error(f"Erro não tratado: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)