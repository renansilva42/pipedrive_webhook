from pipedrive.client import Client
import os
import json

# Configurações
api_token = os.getenv('PIPEDRIVE_API_TOKEN')  # Usando variável de ambiente
company_domain = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')  # Usando variável de ambiente

def get_deal_details(deal_id):
    """Busca todos os detalhes do deal (deal, pessoa, organização, criador, etc.) em uma única requisição usando a biblioteca oficial do Pipedrive."""
    try:
        # Inicializando o cliente do Pipedrive
        client = Client(domain=company_domain)
        client.set_api_token(api_token)

        print(f"Enviando requisição para o deal {deal_id}...")

        # Obtendo todos os dados do deal, incluindo pessoa, organização e criador
        deal = client.deals.get_deal(deal_id)

        # Garantir que estamos incluindo as informações de pessoa e organização
        if not deal:
            print(f"Erro ao obter detalhes do deal: Nenhum dado encontrado")
            return None

        # Logando a resposta completa para depuração
        print("Dados completos do Deal:", json.dumps(deal, indent=2, ensure_ascii=False))

        # Retorna os dados completos do deal
        return deal

    except Exception as err:
        print(f"Falha ao obter detalhes do deal: {str(err)}")
        return None
