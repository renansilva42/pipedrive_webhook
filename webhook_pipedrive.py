from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurações
ACEITE_VERBAL_ID = int(os.getenv('ACEITE_VERBAL_ID'))
ASSINATURA_CONTRATO_ID = int(os.getenv('ASSINATURA_CONTRATO_ID'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
COMPANY_DOMAIN = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')

def get_full_deal_data(deal_id):
    """Busca dados completos do deal incluindo todos os detalhes"""
    url = f'https://{COMPANY_DOMAIN}.pipedrive.com/api/v1/deals/{deal_id}'
    params = {
        'api_token': API_TOKEN
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('data'):
            return result['data']
        print(f"Erro na API: {result.get('error', 'Sem dados')}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {str(e)}")
        return None

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    if 'previous' in data and 'stage_id' in data['previous']:
        current_stage_id = data['data']['stage_id']
        previous_stage_id = data['previous']['stage_id']

        if previous_stage_id == ACEITE_VERBAL_ID and current_stage_id == ASSINATURA_CONTRATO_ID:
            deal_id = data['data']['id']
            print(f"Detectada mudança para assinatura no Deal {deal_id}")
            
            # Busca dados completos
            full_deal = get_full_deal_data(deal_id)
            
            if full_deal:
                try:
                    # Envia payload completo
                    response = requests.post(
                        WEBHOOK_URL,
                        json=full_deal,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        print(f"Dados completos do Deal {deal_id} enviados com sucesso!")
                    else:
                        print(f"Erro no destino: {response.status_code} - {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"Falha no envio: {str(e)}")
            else:
                print(f"Falha ao obter dados do Deal {deal_id}")

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=5000)