# Blockchain-Based File Encryption & Decryption Tool

A comprehensive Flask web application that secures files using three industry-standard symmetric encryption algorithms, with automatic blockchain ledger tracking and performance benchmarking.

## Features

### 🔐 Encryption & Decryption
- **Three Symmetric Algorithms**:
  - AES-256-GCM (Advanced Encryption Standard)
  - Blowfish-256-EAX
  - ChaCha20-Poly1305
- **Secure Key Derivation**: PBKDF2 with SHA-256 (200,000 iterations)
- **Embedded Metadata**: Algorithm, salt, nonce, and authentication tag embedded in encrypted file headers
- **File Download**: Download both encrypted and decrypted files

### ⛓️ Blockchain Ledger
- **Immutable Record**: Every encryption/decryption operation recorded in SQLite blockchain
- **Chain Integrity**: Cryptographic hash chain with prev_hash and tx_hash
- **Searchable**: Filter blockchain records by file name, algorithm, or hash
- **Verification**: Built-in blockchain integrity verification endpoint

### 📊 Performance Benchmarking
- **Automatic Metrics**: Encryption/decryption time and file size tracked automatically
- **Visual Comparison**: Dynamic charts comparing all three algorithms
- **Statistics**: Average performance metrics for each algorithm

## Technical Stack

- **Backend**: Python 3.11 + Flask
- **Cryptography**: PyCryptodome
- **Visualization**: Matplotlib
- **Database**: SQLite
- **Frontend**: HTML5 + Bootstrap 5

## Project Structure

```
.
├── app.py                  # Flask application and API routes
├── crypto_utils.py         # Encryption/decryption logic
├── blockchain.py           # Blockchain ledger management
├── benchmark.py            # Performance chart generation
├── templates/
│   ├── index.html         # Encrypt/decrypt interface
│   ├── benchmark.html     # Performance charts
│   └── ledger.html        # Blockchain viewer
├── storage/
│   ├── encrypted/         # Encrypted files
│   └── decrypted/         # Decrypted files
├── ledger.db              # SQLite blockchain database
└── test_encryption.py     # Algorithm test suite
```

## How It Works

### Encryption Process
1. User uploads file and selects encryption algorithm
2. Passphrase is used with PBKDF2 to derive 256-bit key
3. Random salt and nonce are generated
4. File is encrypted and authenticated
5. Metadata (algorithm ID, salt, nonce, tag) is embedded in file header
6. Encrypted file is saved and available for download
7. Operation is recorded in blockchain ledger

### File Header Format
```
[1 byte: algorithm_id]
[2 bytes: salt_length] [salt]
[2 bytes: nonce_length] [nonce]
[2 bytes: tag_length] [tag]
[remaining bytes: ciphertext]
```

### Decryption Process
1. User uploads encrypted file
2. Metadata is extracted from file header
3. Passphrase derives same 256-bit key using extracted salt
4. File is decrypted using detected algorithm
5. Authentication tag verifies integrity
6. Decrypted file is saved and available for download
7. Decryption time is recorded in blockchain

## API Endpoints

- `GET /` - Main encryption/decryption interface
- `GET /benchmark` - Performance benchmark charts
- `GET /ledger` - Blockchain ledger viewer
- `POST /api/encrypt` - Encrypt file
- `POST /api/decrypt` - Decrypt file
- `GET /api/download/<filename>` - Download file
- `GET /api/benchmark/chart` - Get benchmark chart (base64 PNG)
- `GET /api/benchmark/stats` - Get performance statistics
- `GET /api/ledger` - Get all blockchain blocks
- `GET /api/verify` - Verify blockchain integrity

## Security Notes

⚠️ **Educational Purpose**: This tool is designed for educational demonstration of encryption algorithms and blockchain concepts.

- Passphrases are used only for key derivation and are never stored
- Blockchain stores only metadata (no keys or passphrases)
- All cryptographic operations use industry-standard libraries
- PBKDF2 uses 200,000 iterations for key strengthening

## Testing

Run the included test suite to verify all algorithms:

```bash
python test_encryption.py
```

This tests:
- Encryption with all three algorithms
- Decryption and algorithm detection
- Data integrity verification
- Performance timing

## Usage Example

1. **Encrypt a File**:
   - Click "Choose File" and select your file
   - Select encryption algorithm (AES-256-GCM, Blowfish-256-EAX, or ChaCha20-Poly1305)
   - Enter a strong passphrase
   - Click "Encrypt File"
   - Download the encrypted file

2. **Decrypt a File**:
   - Click "Choose Encrypted File" and select the .enc file
   - Enter the same passphrase
   - Click "Decrypt File"
   - Download the decrypted file

3. **View Performance**:
   - Navigate to "Benchmark" tab
   - View automatic performance comparisons
   - See encryption/decryption times and file sizes

4. **Verify Blockchain**:
   - Navigate to "Blockchain Ledger" tab
   - Click "Verify Integrity" to check blockchain validity
   - Search through all recorded operations

## Requirements

- Python 3.11+
- Flask
- pycryptodome
- matplotlib

## License

Educational demonstration project. Use at your own risk.
