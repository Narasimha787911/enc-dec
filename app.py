import os
import hashlib
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from crypto_utils import encrypt_file, decrypt_file
from blockchain import Blockchain
from benchmark import generate_benchmark_chart, get_benchmark_stats

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'storage'
app.config['ENCRYPTED_FOLDER'] = 'storage/encrypted'
app.config['DECRYPTED_FOLDER'] = 'storage/decrypted'

os.makedirs(app.config['ENCRYPTED_FOLDER'], exist_ok=True)
os.makedirs(app.config['DECRYPTED_FOLDER'], exist_ok=True)

blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/benchmark')
def benchmark():
    return render_template('benchmark.html')

@app.route('/ledger')
def ledger():
    return render_template('ledger.html')

@app.route('/api/encrypt', methods=['POST'])
def api_encrypt():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        passphrase = request.form.get('passphrase')
        algorithm = request.form.get('algorithm')
        
        if not passphrase:
            return jsonify({'error': 'Passphrase is required'}), 400
        
        if algorithm not in ['AES-256-GCM', 'Blowfish-256-EAX', 'ChaCha20-Poly1305']:
            return jsonify({'error': 'Invalid algorithm'}), 400
        
        file_data = file.read()
        original_filename = secure_filename(file.filename)
        
        encrypted_data, enc_time_ms, file_hash, salt, nonce, tag = encrypt_file(
            file_data, passphrase, algorithm
        )
        
        encrypted_filename = f"{os.path.splitext(original_filename)[0]}_encrypted{os.path.splitext(original_filename)[1]}.enc"
        encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        blockchain.add_block(
            algorithm=algorithm,
            file_name=original_filename,
            file_hash=file_hash,
            ciphertext_path=encrypted_path,
            nonce=nonce,
            tag=tag,
            salt=salt,
            file_size_bytes=len(file_data),
            enc_time_ms=enc_time_ms,
            dec_time_ms=None
        )
        
        return jsonify({
            'success': True,
            'message': f'File encrypted successfully using {algorithm}',
            'encrypted_filename': encrypted_filename,
            'enc_time_ms': round(enc_time_ms, 2),
            'file_size_kb': round(len(file_data) / 1024, 2),
            'algorithm': algorithm
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        passphrase = request.form.get('passphrase')
        
        if not passphrase:
            return jsonify({'error': 'Passphrase is required'}), 400
        
        encrypted_data = file.read()
        
        decrypted_data, dec_time_ms, algorithm = decrypt_file(encrypted_data, passphrase)
        
        original_filename = secure_filename(file.filename)
        if original_filename.endswith('.enc'):
            decrypted_filename = original_filename.replace('_encrypted', '').replace('.enc', '')
        else:
            decrypted_filename = f"decrypted_{original_filename}"
        
        decrypted_path = os.path.join(app.config['DECRYPTED_FOLDER'], decrypted_filename)
        
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)
        
        file_hash = hashlib.sha256(decrypted_data).hexdigest()
        blockchain.update_block_dec_time(file_hash, dec_time_ms)
        
        return jsonify({
            'success': True,
            'message': f'File decrypted successfully using {algorithm}',
            'decrypted_filename': decrypted_filename,
            'dec_time_ms': round(dec_time_ms, 2),
            'file_size_kb': round(len(decrypted_data) / 1024, 2),
            'algorithm': algorithm
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<path:filename>')
def download_file(filename):
    try:
        encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], filename)
        decrypted_path = os.path.join(app.config['DECRYPTED_FOLDER'], filename)
        
        if os.path.exists(encrypted_path):
            return send_file(encrypted_path, as_attachment=True, download_name=filename)
        elif os.path.exists(decrypted_path):
            return send_file(decrypted_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/benchmark/chart')
def api_benchmark_chart():
    try:
        chart_base64 = generate_benchmark_chart()
        if chart_base64:
            return jsonify({'success': True, 'chart': chart_base64})
        else:
            return jsonify({'success': False, 'message': 'No data available for benchmark'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/benchmark/stats')
def api_benchmark_stats():
    try:
        stats = get_benchmark_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ledger')
def api_ledger():
    try:
        blocks = blockchain.get_all_blocks()
        return jsonify({'success': True, 'blocks': blocks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify')
def api_verify():
    try:
        is_valid, message = blockchain.verify_chain()
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'message': message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
