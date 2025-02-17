# Arquivo: get_all_deals.py

import requests
import os

# 1. Configuração das credenciais e detalhes da conta

# Obtenha seu token de API do Pipedrive
api_token = 'a90120db9377c335c41700fa6a2a1a4867ff22e4'

# Obtenha seu domínio da empresa Pipedrive
company_domain = 'scmengenharia2'

# 2. Configuração do endpoint

# URL para listar os negócios
url = f'https://{company_domain}.pipedrive.com/api/v1/deals'

# Parâmetros da requisição
params = {
    'limit': 500,  # Limite máximo de itens por página
    'api_token': api_token
}

# 3. Fazendo a chamada à API

print('Enviando requisição...')

# Fazendo a requisição GET
response = requests.get(url, params=params)

# 4. Processando a resposta

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    # Converte a resposta JSON para um dicionário Python
    result = response.json()
    
    # Verifica se há dados retornados
    if not result['data']:
        print('Nenhum negócio criado ainda')
    else:
        # Itera sobre todos os negócios encontrados
        for key, deal in enumerate(result['data'], start=1):
            deal_title = deal['title']
            deal_id = deal['id']
            print(f'#{key} {deal_title} (ID do Negócio: {deal_id})')
else:
    print(f'Erro na requisição: {response.status_code}')
    print(response.text)

# 5. Exemplo completo funcional

# O código acima já é um exemplo completo funcional.
# Para executá-lo, salve-o como 'get_all_deals.py' e execute:
# python get_all_deals.py

# 6. Obtendo todos os negócios com sucesso

# A saída será semelhante ao exemplo fornecido no tutorial original,
# listando todos os negócios com seus títulos e IDs.
