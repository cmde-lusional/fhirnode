import json
import random
from flask import Flask, jsonify

app = Flask(__name__)

def create_protocol_object(fhir_id, fhir_json, permission):
    protocol = {
        "fhir_id": fhir_id,
        "fhir_json": fhir_json,
        "permission": permission
    }
    return protocol

def read_fhir_json_file(file_path):
    with open(file_path, 'r') as f:
        fhir_json = json.load(f)
    return fhir_json

@app.route('/protocol', methods=['GET'])
def get_protocol():
    # Replace with actual FHIR ID
    fhir_id = "sample-fhir-id"
    fhir_json_file_path = 'anonymized_output.json'  # Replace with your FHIR JSON file name

    fhir_json = read_fhir_json_file(fhir_json_file_path)
    permission = random.choice(["download", "read"])

    protocol_object = create_protocol_object(fhir_id, fhir_json, permission)
    return jsonify(protocol_object)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
