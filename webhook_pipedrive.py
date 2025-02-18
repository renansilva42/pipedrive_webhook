from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv  # Adicione esta linha

# Carrega variáveis do .env antes de qualquer configuração
load_dotenv()

app = Flask(__name__)

# Configurações via variáveis de ambiente (agora obrigatórias)
ACEITE_VERBAL_ID = int(os.getenv('ACEITE_VERBAL_ID'))
ASSINATURA_CONTRATO_ID = int(os.getenv('ASSINATURA_CONTRATO_ID'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
COMPANY_DOMAIN = os.getenv('PIPEDRIVE_COMPANY_DOMAIN')

# ... resto do código permanece igual ...
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    if 'previous' in data and 'stage_id' in data['previous']:
        current_stage_id = data['data']['stage_id']
        previous_stage_id = data['previous']['stage_id']

        if previous_stage_id == ACEITE_VERBAL_ID and current_stage_id == ASSINATURA_CONTRATO_ID:
            deal = data['data']
            print(f"Deal {deal['id']} mudou para estágio de assinatura")
            
            try:
                # Envia para webhook externo
                response = requests.post(
                    WEBHOOK_URL,
                    json=deal,
                    headers={'Content-Type': 'application/json'},
                    timeout=5  # Timeout para evitar conexões penduradas
                )
                
                if response.status_code != 200:
                    print(f"Erro no webhook destino: {response.text}")
                
            except requests.exceptions.RequestException as e:
                print(f"Falha na comunicação com webhook: {str(e)}")

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=5000)