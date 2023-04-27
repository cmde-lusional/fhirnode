import psycopg2
import json
import datetime
import base64

def get_data_fhir(table_name, columns):
    query = f"SELECT {', '.join(columns)} FROM {table_name};"
    cursor.execute(query)
    records = cursor.fetchall()

    data = []
    for record in records:
        item = {"resourceType": table_name.capitalize()}
        for i, column in enumerate(columns):
            value = record[i]
            if isinstance(value, datetime.date):
                value = value.isoformat()

            if table_name == "patient" and column == "name":
                item["name"] = [{"text": value}]
            elif table_name == "patient" and column == "telecom":
                if value is not None:
                    item["telecom"] = [{"system": "phone", "value": value}]
                else:
                    item["telecom"] = []
            elif table_name == "patient" and column == "address":
                item["address"] = [{"text": value}]
            elif table_name == "patient" and column == "maritalStatus":
                item["maritalStatus"] = {"text": value}
            elif table_name == "patient" and column == "photo":
                attachment = {}
                if value is None:
                    value = base64.b64encode(b'null').decode('utf-8')
                attachment["data"] = value
                attachment["contentType"] = "application/octet-stream"
                item["photo"] = [attachment]
            elif table_name == "practitioner" and column == "name":
                item["name"] = [{"text": value}]
            elif table_name == "practitioner" and column == "telecom":
                if value is not None:
                    item["telecom"] = [{"system": "phone", "value": value}]
                else:
                    item["telecom"] = []
            elif table_name == "practitioner" and column == "address":
                item["address"] = [{"text": value}]
            elif table_name == "practitioner" and column == "photo":
                attachment = {}
                if value is None:
                    value = base64.b64encode(b'null').decode('utf-8')
                attachment["data"] = value
                attachment["contentType"] = "application/octet-stream"
                item["photo"] = [attachment]
            elif table_name == "encounter" and column in ["subject", "preAdmissionIdentifier", "admissionDestination"]:
                item[column] = {"reference": f"Patient/{value}"} if column == "subject" else {"reference": f"Practitioner/{value}"}
            elif table_name == "observation" and column in ["subject", "encounter", "performer"]:
                reference = "Patient" if column == "subject" else ("Encounter" if column == "encounter" else "Practitioner")
                item[column] = {"reference": f"{reference}/{value}"}
            elif table_name == "diagnosticreport" and column in ["subject", "encounter", "performer"]:
                reference = "Patient" if column == "subject" else ("Encounter" if column == "encounter" else "Practitioner")
                item[column] = {"reference": f"{reference}/{value}"}
            else:
                item[column] = value
        data.append(item)

    return data

def generate_fhir_json(schema):
    fhir_json = {}
    for table_name, columns in schema.items():
        fhir_json[table_name] = get_data_fhir(table_name, columns)
    return fhir_json


if __name__ == "__main__":
    # Connect to your PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="fhir",
        user="postgres",
        password="password"
    )
    cursor = connection.cursor()

    # Schema as a dictionary of lists
    schema = {
        "patient": ["id", "active", "name", "telecom", "gender", "birthDate", "deceasedBoolean", "address", "maritalStatus", "multipleBirthBoolean", "photo"],
        "practitioner": ["id", "active", "name", "telecom", "gender", "birthDate", "address", "photo", "language"], #deceasedBoolean only in R5
        "encounter": ["id", "status", "class", "priority", "type", "subject", "subjectStatus", "serviceProvider", "participantType", "plannedStartDate", "plannedEndDate", "length", "diagnoses", "preAdmissionIdentifier", "admissionDestination"],
        "observation": ["id", "status", "code", "subject", "encounter", "issued", "performer", "valueQuantity", "valueString", "valueBool", "valueInteger", "interpretation", "note", "bodySite", "method", "device"],
        "diagnosticreport": ["id", "status", "code", "subject", "encounter", "issued", "performer", "result", "note", "mediaComment", "mediaLink"]
    }

    fhir_json = generate_fhir_json(schema)
    print(json.dumps(fhir_json, indent=2))

    cursor.close()
    connection.close()