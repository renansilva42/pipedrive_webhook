import requests
import json
import os

# Configurações
api_token = 'a90120db9377c335c41700fa6a2a1a4867ff22e4'  # Substitua pelo seu token de API real
company_domain = 'scmengenharia'  # Substitua pelo seu domínio real, sem 'https://' ou '.pipedrive.com'
deal_id = 1824  # Substitua pelo ID do Deal que você deseja obter detalhes

# Construa a URL
url = f'https://{company_domain}.pipedrive.com/api/v1/deals/{deal_id}?api_token={api_token}'

print('Enviando requisição...')
try:
    response = requests.get(url)
    response.raise_for_status()  # Isso levantará uma exceção para respostas de erro HTTP

    result = response.json()
    
    if not result.get('data'):
        print(f'Erro: {result.get("error", "Nenhum dado encontrado")}')
    else:
        print(f'Aqui estão os detalhes do Deal {result["data"]["id"]}:')
        print(json.dumps(result['data'], indent=2, ensure_ascii=False))
except requests.exceptions.RequestException as e:
    print(f'Erro na requisição: {e}')
except json.JSONDecodeError:
    print('Erro ao decodificar a resposta JSON')
except Exception as e:
    print(f'Ocorreu um erro inesperado: {e}')

# Exemplo usando a biblioteca oficial do Pipedrive (opcional)
# Descomente e instale a biblioteca se desejar usar este método
'''
from pipedrive.client import Client

def get_deal_details():
    try:
        client = Client(domain=company_domain)
        client.set_api_token(api_token)

        print('Enviando requisição...')

        deal = client.deals.get_deal(deal_id)

        print('Deal obtido com sucesso!', json.dumps(deal, indent=2, ensure_ascii=False))
    except Exception as err:
        print('Falha ao obter detalhes do deal', str(err))

get_deal_details()
'''