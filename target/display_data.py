import requests
import json
import sys
import time
import os
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter
from cryptography.fernet import Fernet

TARGETTERMINALNODE_API_URL = "http://localhost:8080/trigger"

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY").encode()
ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY").encode()

def decrypt_api_key():
    cipher_suite = Fernet(ENCRYPTION_KEY)
    decrypted_api_key = cipher_suite.decrypt(ENCRYPTED_API_KEY)
    return decrypted_api_key.decode()

def fetch_data(permission_arg):
    api_key = decrypt_api_key()
    headers = {"X-API-Key": api_key}
    response = requests.get(TARGETTERMINALNODE_API_URL, headers=headers, params={"permission_arg": permission_arg})
    return response.json()

def display_data(data):
    formatted_data = json.dumps(data, indent=2)
    highlighted_data = highlight(formatted_data, JsonLexer(), TerminalFormatter())

    for line in highlighted_data.split('\n'):
        print(line)
        time.sleep(0.1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide an argument: 'read' or 'download'")
        sys.exit(1)
    else:
        permission_arg = sys.argv[1]
    if permission_arg not in ["read", "download"]:
        print('Invalid permission_arg value. Use "read" or "download"')
        sys.exit(1)

    aggregated_data = fetch_data(permission_arg)
    display_data(aggregated_data)
