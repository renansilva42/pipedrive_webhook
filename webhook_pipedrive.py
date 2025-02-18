from flask import Flask, request, jsonify
import logging
import os
import subprocess
from dotenv import load_dotenv

# Configuração
load_dotenv()
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Constantes
ACEITE_VERBAL_ID = int(os.getenv('ACEITE_VERBAL_ID', 4))
ASSINATURA_CONTRATO_ID = int(os.getenv('ASSINATURA_CONTRATO_ID', 5))

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        data = request.json
        logging.info(f"Evento recebido: {data.get('event')}")

        # Verificar estrutura do webhook
        if not all(key in data for key in ['current', 'previous']):
            logging.error("Formato de webhook inválido")
            return jsonify({"status": "invalid format"}), 400

        current = data['current']
        previous = data['previous']
        deal_id = current.get('id')

        # Validar mudança de estágio
        if (previous.get('stage_id') == ACEITE_VERBAL_ID and 
            current.get('stage_id') == ASSINATURA_CONTRATO_ID):
            
            logging.info(f"Detectada mudança válida no deal {deal_id}")
            
            try:
                # Executar script externo
                result = subprocess.run(
                    ['python', 'pega_id_e_envia_dados.py', '--deal-id', str(deal_id)],
                    capture_output=True,
                    text=True
                )
                
                # Log de saídas
                logging.info(f"Saída do script:\n{result.stdout}")
                if result.stderr:
                    logging.error(f"Erros do script:\n{result.stderr}")
                
                return jsonify({"status": "processed"}), 200
            
            except Exception as e:
                logging.error(f"Erro ao executar script: {str(e)}")
                return jsonify({"status": "script error"}), 500

        return jsonify({"status": "ignored"}), 200

    except Exception as e:
        logging.error(f"Erro crítico: {str(e)}")
        return jsonify({"status": "server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)