import requests
import json
import tkinter as tk
from tkinter import Text


def fetch_data():
    # Replace with your actual endpoints
    endpoints = []
    for i in range(0, 9):
        endpoints.append(f'http://localhost:{5000 + i}/protocol')

    aggregated_data = []

    for url in endpoints:
        response = requests.get(url)
        data = response.json()

        # Create a dictionary for the data from this endpoint
        endpoint_data = {
            "fhir_id": data["fhir_id"],
            "fhir_json": data["fhir_json"],
            "permission": data["permission"]
        }

        # Append the dictionary to the list of aggregated data
        aggregated_data.append(endpoint_data)

    return aggregated_data


def display_data(data):
    window = tk.Tk()
    window.title("Aggregated Data")

    text_widget = Text(window, wrap="word", padx=10, pady=10)
    text_widget.insert("1.0", json.dumps(data, indent=4))
    text_widget.configure(state="disabled")  # Make the text widget read-only
    text_widget.pack(expand=True, fill="both")

    # Disable copy functionality by intercepting the Copy event
    window.bind_all("<<Copy>>", lambda event: "break")

    window.mainloop()


if __name__ == '__main__':
    aggregated_data = fetch_data()
    display_data(aggregated_data)
