#### this script takes in a string (the api key) and uses cryptography to generate an encrypted key and the encryption key

from cryptography.fernet import Fernet

api_key = "your_api_key"
# Generate an encryption key (keep this safe, it'll be used for both encryption and decryption)
encryption_key = Fernet.generate_key()

# Create a Fernet instance with the encryption key
cipher_suite = Fernet(encryption_key)

# Encrypt the API key
encrypted_api_key = cipher_suite.encrypt(api_key.encode())

print("Encryption key:", encryption_key)
print("Encrypted API key:", encrypted_api_key)