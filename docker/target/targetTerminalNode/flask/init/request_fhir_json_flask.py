import sys
import os
import requests
import json
from flask import Flask, request, jsonify

api_key_os = os.environ.get("API_KEY")

app = Flask(__name__)

def fetch_data(permission_arg):
    # Replace with your actual endpoints
    endpoints = []
    for i in range(0, 9):
        ## FIXMEEEEE!!!!
        endpoints.append(f'http://host.docker.internal:{5000 + i}/protocol')
        ##if script is running on localhost directly and not in container:
        #endpoints.append(f'http://localhost:{5000+i}/protocol')

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

        #with open('aggregated_data.json', 'w') as outfile:
        #    json.dump(aggregated_data, outfile, indent=4)

        return aggregated_data


@app.route('/trigger', methods=['GET'])
def trigger():
    api_key = request.headers.get("X-API-Key")
    if api_key != api_key_os:
        return "Unauthorized", 401

    permission_arg = request.args.get('permission_arg', None)

    if permission_arg not in ["read", "download"]:
        return 'Invalid permission_arg value. Use "read" or "download"', 400
    else:
        aggregated_data = fetch_data(permission_arg)
        return jsonify(aggregated_data), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
