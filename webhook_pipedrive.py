from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configurações (use variáveis de ambiente em produção)
ACEITE_VERBAL_ID = int(os.getenv('ACEITE_VERBAL_ID', 4))
ASSINATURA_CONTRATO_ID = int(os.getenv('ASSINATURA_CONTRATO_ID', 5))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://seu-webhook-destino.com/endpoint')

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