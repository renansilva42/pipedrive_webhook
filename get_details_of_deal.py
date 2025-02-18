import requests
import json
import os

# Configurações
api_token = os.getenv('PIPEDRIVE_API_TOKEN')  # Agora usando variável de ambiente
company_domain = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')  # Usando variável de ambiente

def get_deal_details(deal_id):
    """Busca todos os detalhes de um deal específico."""
    url = f'https://{company_domain}.pipedrive.com/api/v1/deals/{deal_id}?api_token={api_token}'

    try:
        print('Enviando requisição para Pipedrive...')
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção para respostas de erro HTTP
        
        result = response.json()
        
        if not result.get('data'):
            print(f'Erro: {result.get("error", "Nenhum dado encontrado")}')
            return None
        else:
            return result['data']

    except requests.exceptions.RequestException as e:
        print(f'Erro na requisição: {e}')
        return None
    except json.JSONDecodeError:
        print('Erro ao decodificar a resposta JSON')
        return None
    except Exception as e:
        print(f'Ocorreu um erro inesperado: {e}')
        return None
