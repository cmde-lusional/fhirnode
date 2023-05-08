import json
from faker import Faker

fake = Faker()

def anonymize_resource(resource):
    if resource["resourceType"] in ["Patient", "Practitioner"]:
        resource["name"] = [{"text": fake.name()}]
        resource["telecom"] = [{"system": "phone", "value": fake.phone_number()}]
        resource["address"] = [{"text": fake.address()}]
        resource["photo"] = [{"data": "bnVsbA==", "contentType": "application/octet-stream"}]
    return resource

def anonymize_fhir_json(fhir_json):
    for resource_type in fhir_json:
        fhir_json[resource_type] = [anonymize_resource(resource) for resource in fhir_json[resource_type]]
    return fhir_json

# Load your FHIR JSON example from a file
with open("output.json", "r") as infile:
    fhir_json_example = json.load(infile)

# Anonymize the FHIR JSON
anonymized_fhir_json = anonymize_fhir_json(fhir_json_example)

# Save the anonymized FHIR JSON to a new file
with open("anonymized_output.json", "w") as outfile:
    json.dump(anonymized_fhir_json, outfile, indent=2)