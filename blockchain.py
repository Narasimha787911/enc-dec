import sqlite3
import hashlib
import json
from datetime import datetime
import base64

class Blockchain:
    def __init__(self, db_path='ledger.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                index INTEGER PRIMARY KEY,
                timestamp TEXT,
                prev_hash TEXT,
                tx_hash TEXT,
                algorithm TEXT,
                file_name TEXT,
                file_hash TEXT,
                ciphertext_path TEXT,
                nonce_b64 TEXT,
                tag_b64 TEXT,
                salt_b64 TEXT,
                file_size_bytes INTEGER,
                enc_time_ms REAL,
                dec_time_ms REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_last_block(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM blocks ORDER BY index DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'index': row[0],
                'timestamp': row[1],
                'prev_hash': row[2],
                'tx_hash': row[3],
                'algorithm': row[4],
                'file_name': row[5],
                'file_hash': row[6],
                'ciphertext_path': row[7],
                'nonce_b64': row[8],
                'tag_b64': row[9],
                'salt_b64': row[10],
                'file_size_bytes': row[11],
                'enc_time_ms': row[12],
                'dec_time_ms': row[13]
            }
        return None
    
    def calculate_hash(self, block_data):
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def add_block(self, algorithm, file_name, file_hash, ciphertext_path, 
                  nonce, tag, salt, file_size_bytes, enc_time_ms, dec_time_ms=None):
        last_block = self.get_last_block()
        
        if last_block:
            index = last_block['index'] + 1
            prev_hash = last_block['tx_hash']
        else:
            index = 0
            prev_hash = '0' * 64
        
        timestamp = datetime.utcnow().isoformat()
        
        nonce_b64 = base64.b64encode(nonce).decode('utf-8')
        tag_b64 = base64.b64encode(tag).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        
        block_data = {
            'index': index,
            'timestamp': timestamp,
            'prev_hash': prev_hash,
            'algorithm': algorithm,
            'file_name': file_name,
            'file_hash': file_hash,
            'ciphertext_path': ciphertext_path,
            'nonce_b64': nonce_b64,
            'tag_b64': tag_b64,
            'salt_b64': salt_b64,
            'file_size_bytes': file_size_bytes,
            'enc_time_ms': enc_time_ms,
            'dec_time_ms': dec_time_ms if dec_time_ms is not None else 0.0
        }
        
        tx_hash = self.calculate_hash(block_data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blocks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            index, timestamp, prev_hash, tx_hash,
            algorithm, file_name, file_hash, ciphertext_path,
            nonce_b64, tag_b64, salt_b64, file_size_bytes,
            enc_time_ms, dec_time_ms if dec_time_ms is not None else 0.0
        ))
        conn.commit()
        conn.close()
        
        return tx_hash
    
    def update_block_dec_time(self, file_hash, dec_time_ms):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE blocks SET dec_time_ms = ? WHERE file_hash = ? AND dec_time_ms = 0.0
        ''', (dec_time_ms, file_hash))
        conn.commit()
        conn.close()
    
    def get_all_blocks(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM blocks ORDER BY index ASC')
        rows = cursor.fetchall()
        conn.close()
        
        blocks = []
        for row in rows:
            blocks.append({
                'index': row[0],
                'timestamp': row[1],
                'prev_hash': row[2],
                'tx_hash': row[3],
                'algorithm': row[4],
                'file_name': row[5],
                'file_hash': row[6],
                'ciphertext_path': row[7],
                'nonce_b64': row[8],
                'tag_b64': row[9],
                'salt_b64': row[10],
                'file_size_bytes': row[11],
                'enc_time_ms': row[12],
                'dec_time_ms': row[13]
            })
        return blocks
    
    def verify_chain(self):
        blocks = self.get_all_blocks()
        
        if not blocks:
            return True, "Blockchain is empty"
        
        for i, block in enumerate(blocks):
            if i == 0:
                if block['prev_hash'] != '0' * 64:
                    return False, f"Genesis block has invalid prev_hash"
            else:
                if block['prev_hash'] != blocks[i-1]['tx_hash']:
                    return False, f"Block {i} has broken chain link"
            
            block_data = {
                'index': block['index'],
                'timestamp': block['timestamp'],
                'prev_hash': block['prev_hash'],
                'algorithm': block['algorithm'],
                'file_name': block['file_name'],
                'file_hash': block['file_hash'],
                'ciphertext_path': block['ciphertext_path'],
                'nonce_b64': block['nonce_b64'],
                'tag_b64': block['tag_b64'],
                'salt_b64': block['salt_b64'],
                'file_size_bytes': block['file_size_bytes'],
                'enc_time_ms': block['enc_time_ms'],
                'dec_time_ms': block['dec_time_ms']
            }
            
            calculated_hash = self.calculate_hash(block_data)
            if calculated_hash != block['tx_hash']:
                return False, f"Block {i} has invalid transaction hash"
        
        return True, f"Blockchain is valid ({len(blocks)} blocks verified)"
