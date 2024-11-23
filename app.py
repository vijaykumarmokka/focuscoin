import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from web3 import Web3
from dotenv import load_dotenv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB files

load_dotenv()

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_NETWORK_RPC')))
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
CONTRACT_ABI = [
    # Paste your contract ABI here
]
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'url': f'/uploads/{filename}'}), 200

@app.route('/analyze_smile', methods=['POST'])
def analyze_smile():
    data = request.json
    image_url = data.get('image_url')
    if not image_url:
        return jsonify({'error': 'Image URL is required'}), 400
    try:
        oracle_fee = contract.functions.getOracleFee().call()
        txn = contract.functions.analyzeSmile(image_url).buildTransaction({
            'gas': 500000,
            'value': oracle_fee,
        })
        # Add signer logic for sending transaction
        return jsonify({'message': 'Smile analysis submitted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
