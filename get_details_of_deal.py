import requests
import json
import os

# Configurações
api_token = os.getenv('PIPEDRIVE_API_TOKEN')  # Usando variável de ambiente
company_domain = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')  # Usando variável de ambiente

def get_deal_details(deal_id):
    """Busca todos os detalhes de um deal específico, incluindo pessoa, organização e criador."""
    # URL da API para o deal
    url = f'https://{company_domain}.pipedrive.com/api/v1/deals/{deal_id}?api_token={api_token}'
    try:
        # Requisição para obter os dados do deal
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()

        if not result.get('data'):
            print(f"Erro ao obter dados do deal: {result.get('error', 'Sem dados')}")
            return None
        else:
            deal_data = result['data']

            # Buscar dados sobre a pessoa
            person_data = {}
            if 'person_id' in deal_data:
                person_url = f'https://{company_domain}.pipedrive.com/api/v1/persons/{deal_data["person_id"]}?api_token={api_token}'
                person_response = requests.get(person_url)
                person_data = person_response.json().get('data', {})

            # Buscar dados sobre a organização
            org_data = {}
            if 'org_id' in deal_data:
                org_url = f'https://{company_domain}.pipedrive.com/api/v1/organizations/{deal_data["org_id"]}?api_token={api_token}'
                org_response = requests.get(org_url)
                org_data = org_response.json().get('data', {})

            # Buscar dados sobre o criador do deal
            creator_data = {}
            if 'creator_user_id' in deal_data:
                creator_url = f'https://{company_domain}.pipedrive.com/api/v1/users/{deal_data["creator_user_id"]}?api_token={api_token}'
                creator_response = requests.get(creator_url)
                creator_data = creator_response.json().get('data', {})

            # Combina todos os dados em um único objeto
            full_deal_data = {
                "deal": deal_data,
                "person": person_data,
                "organization": org_data,
                "creator_user": creator_data
            }

            return full_deal_data
    except requests.exceptions.RequestException as e:
        print(f'Erro na requisição para o deal {deal_id}: {str(e)}')
        return None
