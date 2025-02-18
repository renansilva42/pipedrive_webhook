import requests
import os

# Configurações
api_token = os.getenv('PIPEDRIVE_API_TOKEN')
company_domain = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')

def get_deal_details(deal_id):
    """Busca todos os detalhes do deal (deal, pessoa, organização, criador, etc.) em uma única requisição."""
    url = f'https://{company_domain}.pipedrive.com/api/v1/deals/{deal_id}?api_token={api_token}&include_persons=1&include_organizations=1'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve erro na requisição
        result = response.json()

        if not result.get('data'):
            print(f"Erro: {result.get('error', 'Sem dados')}")
            return None
        else:
            deal_data = result['data']
            full_deal_data = {
                "deal": deal_data,
                "person": deal_data.get('person', {}),
                "organization": deal_data.get('organization', {}),
                "creator_user": deal_data.get('creator_user', {})
            }
            return full_deal_data
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para o deal {deal_id}: {str(e)}")
        return None