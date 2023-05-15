import requests
import json
import sys
import time
import os
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox, filedialog

#URL for the endpoint of the closed docker container targetterminalnode which ones it is triggered will request
#all the data from the sourceterminalnodes
TARGETTERMINALNODE_API_URL = "http://localhost:8080/trigger"

#this encryption key is used to make it only for the program possible to use the http endpoint of the closed
#targetterminalnode
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY").encode()
ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY").encode()

#this function uses the ENCRYPTION_KEY to decrypt the ENCRYPTED_API_KEY to receive the real api key
def decrypt_api_key():
    cipher_suite = Fernet(ENCRYPTION_KEY)
    decrypted_api_key = cipher_suite.decrypt(ENCRYPTED_API_KEY)
    return decrypted_api_key.decode()

#with the api key and a permission (which is the user input in form of an argument from the command line
#we can now fetch the data from the endpoint
def fetch_data(permission_arg):
    api_key = decrypt_api_key()
    headers = {"X-API-Key": api_key}
    response = requests.get(TARGETTERMINALNODE_API_URL, headers=headers, params={"permission_arg": permission_arg})
    return response.json()

#depending on how the permission is set from the user the display function will either only display the data
#using the tkwinter library or it will provide an option for downloading it, this will be more expensive in later
#adding the blockchain
def display_data(data, permission_arg):
    formatted_data = json.dumps(data, indent=2)

    def save_data():
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            with open(file_path, "w") as file:
                file.write(formatted_data)

    root = tk.Tk()
    root.title("JSON Data Viewer")
    text_widget = tk.Text(root, wrap=tk.WORD, bg=root.cget("bg"), relief=tk.FLAT)
    text_widget.insert(tk.END, formatted_data)
    text_widget.pack(expand=True, fill=tk.BOTH)

    if permission_arg == "read":
        text_widget.config(state=tk.DISABLED)
    elif permission_arg == "download":
        save_button = tk.Button(root, text="Save Data", command=save_data)
        save_button.pack()

    root.mainloop()

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
    display_data(aggregated_data, permission_arg)
