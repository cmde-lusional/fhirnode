import sys
import requests
import json

def fetch_data(permission_arg):
    # Replace with your actual endpoints
    endpoints = []
    for i in range(0, 9):
        endpoints.append(f'http://localhost:{5000+i}/protocol')

    # Create two empty arrays for data of different permission levels
    aggregated_data = []

    for url in endpoints:
        response = requests.get(url)
        data = response.json()

        # Create dictionaries for the data from this endpoint for permission levels
        if data["permission"] == permission_arg:
            endpoint_data = {
                "fhir_id": data["fhir_id"],
                "fhir_json": data["fhir_json"],
                "permission": data["permission"]
            }
        else:
            endpoint_data = {}

        # Append the dictionary to the list of aggregated data but don't add a dic if the dic is empty
        if len(endpoint_data) != 0:
            aggregated_data.append(endpoint_data)
        else:
            continue

        with open('aggregated_data.json', 'w') as outfile:
            json.dump(aggregated_data, outfile, indent=4)

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ["read", "download"]:
        print("Usage: python3 script_name.py [read|download]")
    else:
        permission_arg = sys.argv[1]
        fetch_data(permission_arg)
