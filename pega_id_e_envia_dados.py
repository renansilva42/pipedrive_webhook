# import requests
# import json
# import sys  # Adicionado para ler parâmetros

# # Configurações FIXAS conforme seu exemplo
# api_token = 'a90120db9377c335c41700fa6a2a1a4867ff22e4'
# company_domain = 'scmengenharia'
# webhook_url = 'https://hook.us2.make.com/q6zasmovveyi4xsiv5vd4bxf4uegvy5o'

# # Obtém o deal_id da linha de comando
# if len(sys.argv) < 2:
#     print("Erro: É necessário fornecer o deal_id como parâmetro")
#     print("Uso: python pega_id_e_envia_dados.py <deal_id>")
#     exit(1)

# deal_id = sys.argv[1]

# # Restante do código igual ao seu exemplo original
# pipedrive_url = f'https://{company_domain}.pipedrive.com/api/v1/deals/{deal_id}?api_token={api_token}'

# print('Enviando requisição para Pipedrive...')

# try:
#     # Buscar dados do deal
#     response = requests.get(pipedrive_url)
#     response.raise_for_status()
#     result = response.json()
    
#     if not result.get('data'):
#         print(f'Erro: {result.get("error", "Nenhum dado encontrado")}')
#         exit()

#     deal_data = result['data']
#     print(f'Dados do Deal {deal_id} obtidos com sucesso!')
    
#     # Enviar para webhook
#     print(f'Enviando para webhook: {webhook_url}')
#     webhook_response = requests.post(
#         webhook_url,
#         json=deal_data,
#         headers={'Content-Type': 'application/json'}
#     )
    
#     # Verificar resposta do webhook
#     if webhook_response.status_code == 200:
#         print('Dados enviados para webhook com sucesso!')
#         print('Resposta do webhook:', webhook_response.text)
#     else:
#         print(f'Erro no webhook: {webhook_response.status_code}')
#         print('Detalhes:', webhook_response.text)

# except requests.exceptions.RequestException as e:
#     print(f'Erro na requisição: {e}')
# except json.JSONDecodeError:
#     print('Erro ao decodificar a resposta JSON')
# except Exception as e:
#     print(f'Ocorreu um erro inesperado: {e}')