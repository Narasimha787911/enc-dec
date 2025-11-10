import os
import struct
import hashlib
import time
from Crypto.Cipher import AES, Blowfish, ChaCha20_Poly1305
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

ALGORITHM_IDS = {
    'AES-256-GCM': 1,
    'Blowfish-256-EAX': 2,
    'ChaCha20-Poly1305': 3
}

ALGORITHM_NAMES = {v: k for k, v in ALGORITHM_IDS.items()}

def derive_key(passphrase, salt):
    return PBKDF2(passphrase, salt, dkLen=32, count=200000, hmac_hash_module=hashlib.sha256)

def encrypt_file(file_data, passphrase, algorithm):
    start_time = time.perf_counter()
    
    salt = get_random_bytes(16)
    key = derive_key(passphrase, salt)
    
    algorithm_id = ALGORITHM_IDS[algorithm]
    
    if algorithm == 'AES-256-GCM':
        nonce = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(file_data)
    elif algorithm == 'Blowfish-256-EAX':
        cipher = Blowfish.new(key, Blowfish.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(file_data)
    elif algorithm == 'ChaCha20-Poly1305':
        nonce = get_random_bytes(12)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        ciphertext = cipher.encrypt(file_data)
        tag = cipher.digest()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    header = struct.pack('B', algorithm_id)
    header += struct.pack('H', len(salt)) + salt
    header += struct.pack('H', len(nonce)) + nonce
    header += struct.pack('H', len(tag)) + tag
    
    encrypted_data = header + ciphertext
    
    end_time = time.perf_counter()
    enc_time_ms = (end_time - start_time) * 1000
    
    file_hash = hashlib.sha256(file_data).hexdigest()
    
    return encrypted_data, enc_time_ms, file_hash, salt, nonce, tag

def decrypt_file(encrypted_data, passphrase):
    start_time = time.perf_counter()
    
    offset = 0
    algorithm_id = struct.unpack('B', encrypted_data[offset:offset+1])[0]
    offset += 1
    
    algorithm = ALGORITHM_NAMES.get(algorithm_id)
    if not algorithm:
        raise ValueError(f"Unknown algorithm ID: {algorithm_id}")
    
    salt_len = struct.unpack('H', encrypted_data[offset:offset+2])[0]
    offset += 2
    salt = encrypted_data[offset:offset+salt_len]
    offset += salt_len
    
    nonce_len = struct.unpack('H', encrypted_data[offset:offset+2])[0]
    offset += 2
    nonce = encrypted_data[offset:offset+nonce_len]
    offset += nonce_len
    
    tag_len = struct.unpack('H', encrypted_data[offset:offset+2])[0]
    offset += 2
    tag = encrypted_data[offset:offset+tag_len]
    offset += tag_len
    
    ciphertext = encrypted_data[offset:]
    
    key = derive_key(passphrase, salt)
    
    if algorithm == 'AES-256-GCM':
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    elif algorithm == 'Blowfish-256-EAX':
        cipher = Blowfish.new(key, Blowfish.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    elif algorithm == 'ChaCha20-Poly1305':
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        cipher.verify(tag)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    end_time = time.perf_counter()
    dec_time_ms = (end_time - start_time) * 1000
    
    return plaintext, dec_time_ms, algorithm
