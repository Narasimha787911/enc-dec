#!/usr/bin/env python3
"""
Test script to verify all three encryption algorithms work correctly
"""
import os
import sys
from crypto_utils import encrypt_file, decrypt_file

def test_algorithm(algorithm, test_data, passphrase):
    print(f"\nTesting {algorithm}...")
    
    try:
        encrypted_data, enc_time_ms, file_hash, salt, nonce, tag = encrypt_file(
            test_data, passphrase, algorithm
        )
        print(f"  ✓ Encryption successful ({enc_time_ms:.2f} ms)")
        print(f"  - File hash: {file_hash[:16]}...")
        print(f"  - Encrypted size: {len(encrypted_data)} bytes")
        
        decrypted_data, dec_time_ms, detected_algorithm = decrypt_file(
            encrypted_data, passphrase
        )
        print(f"  ✓ Decryption successful ({dec_time_ms:.2f} ms)")
        print(f"  - Detected algorithm: {detected_algorithm}")
        
        if decrypted_data == test_data:
            print(f"  ✓ Data integrity verified")
        else:
            print(f"  ✗ Data mismatch!")
            return False
        
        if detected_algorithm == algorithm:
            print(f"  ✓ Algorithm detection correct")
        else:
            print(f"  ✗ Algorithm detection failed!")
            return False
        
        print(f"  ✓ {algorithm} test PASSED")
        return True
        
    except Exception as e:
        print(f"  ✗ {algorithm} test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Blockchain-Based File Encryption Tool - Algorithm Test")
    print("=" * 60)
    
    test_data = b"This is a test file for verifying encryption algorithms work correctly!"
    passphrase = "test_password_123"
    
    results = {}
    
    for algorithm in ['AES-256-GCM', 'Blowfish-256-EAX', 'ChaCha20-Poly1305']:
        results[algorithm] = test_algorithm(algorithm, test_data, passphrase)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for algorithm, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{algorithm}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✓ All tests passed successfully!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
