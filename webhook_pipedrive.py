from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    # Verifica se é uma mudança de estágio 4 → 5
    if (data.get('previous', {}).get('stage_id') == 4 and 
        data.get('current', {}).get('stage_id') == 5):
        
        deal_id = data.get('current', {}).get('id')
        
        if deal_id:
            # Chama o outro script passando o deal_id como parâmetro
            try:
                subprocess.run(['python', 'pega_id_e_envia_dados.py', str(deal_id)])
                return 'Processado com sucesso', 200
            except Exception as e:
                return f'Erro ao executar script: {str(e)}', 500
    
    return 'Ignorado - Não é mudança 4→5', 200

if __name__ == '__main__':
    app.run(port=5000)