# Blockchain-Based File Encryption and Decryption Tool

## Overview
A Flask web application that encrypts and decrypts files using three symmetric encryption algorithms:
- AES-256-GCM
- Blowfish-256-EAX
- ChaCha20-Poly1305

Each operation is recorded in an immutable blockchain ledger, and performance metrics are automatically tracked and visualized.

## Project Architecture

### Backend (Python/Flask)
- `app.py` - Main Flask application with API routes
- `crypto_utils.py` - Encryption/decryption logic with PBKDF2 key derivation
- `blockchain.py` - SQLite-based blockchain ledger management
- `benchmark.py` - Performance chart generation using matplotlib

### Frontend (HTML/Bootstrap)
- `templates/index.html` - Encrypt/decrypt interface
- `templates/benchmark.html` - Performance comparison charts
- `templates/ledger.html` - Blockchain ledger viewer

### Storage
- `storage/encrypted/` - Encrypted files
- `storage/decrypted/` - Decrypted files
- `ledger.db` - SQLite blockchain database

## Key Features
1. File encryption/decryption with metadata embedded in encrypted file headers
2. Automatic blockchain ledger recording
3. Real-time performance benchmarking with matplotlib charts
4. Blockchain integrity verification
5. Purple gradient UI matching design specifications

## Recent Changes
- Initial project setup (2024-11-10)
- Implemented all three encryption algorithms
- Created blockchain ledger system
- Built responsive UI with Bootstrap
- Configured Flask workflow on port 5000

## Technical Details
- Python 3.11+
- PBKDF2 key derivation (SHA-256, 200k iterations)
- File header format: algorithm_id | salt_len | salt | nonce_len | nonce | tag_len | tag | ciphertext
- Blockchain stores metadata only (no keys or passphrases)
