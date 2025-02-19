from pipedrive.client import Client
import os
import json
import requests

# Configurações
api_token = os.getenv('PIPEDRIVE_API_TOKEN')  # Obtendo o token de API da variável de ambiente
company_domain = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')  # Domínio da empresa no Pipedrive
WEBHOOK_URL = "https://hook.us2.make.com/q6zasmovveyi4xsiv5vd4bxf4uegvy5o"  # URL do webhook externo

def get_deal_details(deal_id):
    try:
        # Inicializando o cliente do Pipedrive sem o parâmetro 'domain'
        client = Client()
        client.set_api_token(api_token)  # Configura o token de API

        print(f"Enviando requisição para o deal {deal_id}...")

        # Requisição para obter os detalhes do deal
        deal = client.deals.get_deal(deal_id)

        if not deal:
            print(f"Erro ao obter detalhes do deal: Nenhum dado encontrado")
            return None

        print("Dados completos do Deal:", json.dumps(deal, indent=2, ensure_ascii=False))

        # Enviar os dados do deal para o webhook
        response = requests.post(WEBHOOK_URL, json=deal, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            print(f"Dados do Deal {deal_id} enviados com sucesso para o webhook!")
        else:
            print(f"Erro ao enviar dados para o webhook: {response.status_code} - {response.text}")

        return deal  # Retorna os dados completos do deal

    except Exception as err:
        print(f"Falha ao obter detalhes do deal: {str(err)}")
        return None
