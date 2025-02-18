import requests
import json
import os
import argparse

def enviar_dados_do_deal(deal_id):
    # Configurações do .env
    api_token = os.getenv('PIPEDRIVE_API_TOKEN')
    company_domain = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')
    webhook_url = os.getenv('WEBHOOK_URL')

    # Construa a URL do Pipedrive
    pipedrive_url = f'https://{company_domain}.pipedrive.com/api/v1/deals/{deal_id}?api_token={api_token}'

    print(f'Processando deal {deal_id}...')

    try:
        # Buscar dados do deal
        response = requests.get(pipedrive_url)
        response.raise_for_status()
        result = response.json()
        
        if not result.get('data'):
            print(f'Erro: {result.get("error", "Nenhum dado encontrado")}')
            return False

        deal_data = result['data']
        print(f'Dados do Deal {deal_id} obtidos com sucesso!')
        
        # Enviar para webhook
        print(f'Enviando para webhook: {webhook_url}')
        webhook_response = requests.post(
            webhook_url,
            json=deal_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Verificar resposta do webhook
        if webhook_response.status_code == 200:
            print('Dados enviados para webhook com sucesso!')
            print('Resposta do webhook:', webhook_response.text)
            return True
        else:
            print(f'Erro no webhook: {webhook_response.status_code}')
            print('Detalhes:', webhook_response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f'Erro na requisição: {e}')
        return False
    except json.JSONDecodeError:
        print('Erro ao decodificar a resposta JSON')
        return False
    except Exception as e:
        print(f'Ocorreu um erro inesperado: {e}')
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processa um deal do Pipedrive')
    parser.add_argument('--deal-id', type=int, required=True, help='ID do deal a ser processado')
    args = parser.parse_args()
    
    enviar_dados_do_deal(args.deal_id)