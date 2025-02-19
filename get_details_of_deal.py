import os
import json
import requests

# Configurações
api_token = os.getenv('PIPEDRIVE_API_TOKEN')
company_domain = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')
WEBHOOK_URL = "https://hook.us2.make.com/q6zasmovveyi4xsiv5vd4bxf4uegvy5o"

def get_deal_details(deal_id):
    try:
        # Construção da URL para a requisição
        url = f'https://{company_domain}.pipedrive.com/api/v1/deals/{deal_id}?api_token={api_token}'
        print(f"Enviando requisição para o deal {deal_id}...")

        # Requisição HTTP para obter detalhes do deal
        response = requests.get(url)
        response.raise_for_status()
        deal = response.json().get('data')

        if not deal:
            print("Erro: Nenhum dado encontrado para este deal.")
            return None

        print("Dados completos do Deal:", json.dumps(deal, indent=2, ensure_ascii=False))

        # Enviar os dados do deal para o webhook
        webhook_response = requests.post(WEBHOOK_URL, json=deal, headers={'Content-Type': 'application/json'})
        if webhook_response.status_code == 200:
            print(f"Dados do Deal {deal_id} enviados com sucesso para o webhook!")
        else:
            print(f"Erro ao enviar dados para o webhook: {webhook_response.status_code} - {webhook_response.text}")

        return deal
    except requests.exceptions.RequestException as err:
        print(f"Falha ao obter detalhes do deal: {str(err)}")
        return None
