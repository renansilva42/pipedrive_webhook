from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configure os IDs dos estágios (substitua com os seus IDs)
ACEITE_VERBAL_ID = 4  
ASSINATURA_CONTRATO_ID = 5

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json

    # Verifica se é uma mudança de estágio
    if 'previous' in data and 'stage_id' in data['previous']:
        current_stage_id = data['data']['stage_id']
        previous_stage_id = data['previous']['stage_id']

        # Filtra a mudança específica: Aceite Verbal → Assinatura do Contrato
        if previous_stage_id == ACEITE_VERBAL_ID and current_stage_id == ASSINATURA_CONTRATO_ID:
            deal = data['data']
            print("Mudança de estágio detectada!")
            print("Dados completos do deal:", deal)

            # Aqui você pode adicionar ações (ex: enviar para outro sistema)
            # ...

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)