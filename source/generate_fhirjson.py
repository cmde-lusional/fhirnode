import psycopg2
import json
import datetime
import base64

def get_data_fhir(table_name, columns):
    query = f"SELECT {', '.join(columns)} FROM {table_name};"
    cursor.execute(query)
    records = cursor.fetchall()

    # handle first character of table name to uppercase for creation of fhir resource name
    capitalized_first_char = table_name[0].upper()
    table_name_capitalized = capitalized_first_char + table_name[1:]

    data = []
    for record in records:
        item = {"resourceType": table_name_capitalized }
        for i, column in enumerate(columns):
            value = record[i]
            if isinstance(value, datetime.date):
                value = value.isoformat()

            ###PATIENT RULES
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

            ###PRACTITIONER RULES
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

            ###MEDIA RULES
            elif table_name == "media" and column == "content":
                attachment = {}
                if value is not None:
                    value = base64.b64encode(value.tobytes()).decode('utf-8')
                else:
                    value = base64.b64encode(b'null').decode('utf-8')
                attachment["data"] = value
                item["content"] = attachment

            ###ENCOUNTER RULES
            elif table_name == "encounter" and column == "class":
                item["class"] = {"code": value}
            elif table_name == "encounter" and column == "type":
                item["type"] = [{"text": value}]
            elif table_name == "encounter" and column == "priority":
                item["priority"] = {"text": value}
            elif table_name == "encounter" and column == "subject":
                if value is not None:
                    item["subject"] = {"reference": f"Patient/{value}"}
            elif table_name == "encounter" and column in ["preAdmissionIdentifier", "destination"]:
                if "hospitalization" not in item:
                    item["hospitalization"] = {}
                if column == "preAdmissionIdentifier" and value is not None:
                    item["hospitalization"]["preAdmissionIdentifier"] = {"value": value}
                elif column == "destination" and value is not None:
                    item["hospitalization"]["destination"] = {"reference": f"{value}"}
            elif table_name == "encounter" and column == "length":
                item["length"] = {"value": value, "unit": "minutes", "code": "min",
                                  "system": "http://unitsofmeasure.org"}
            elif table_name == "encounter" and column == "serviceProvider":
                item["serviceProvider"] = {"reference": f"Organization/{value}"}
            elif table_name == "encounter" and column in ["subject", "preAdmissionIdentifier", "destination"]:
                item[column] = {"reference": f"{value}"} if column == "subject" else {"reference": f"{value}"}
            elif table_name == "encounter" and (column == "participantType" or column == "participantID"):
                if "participant" not in item:
                    item["participant"] = []
                    participant_added = False  # Add a flag variable here
                if not participant_added:
                    if record[columns.index("participantID")] is not None and record[
                        columns.index("participantType")] is not None:
                        item["participant"].append({
                            "type": [{"text": record[columns.index('participantType')]}],
                            "individual": {"reference": f"Practitioner/{record[columns.index('participantID')]}"}
                        })
                        participant_added = True
                    elif record[columns.index("participantID")] is None and record[
                        columns.index("participantType")] is not None:
                        item["participant"].append({
                            "type": [{"text": record[columns.index('participantType')]}],
                            "individual": {"reference": "not given"}
                        })
                        participant_added = True
                    elif record[columns.index("participantID")] is not None and record[
                        columns.index("participantType")] is None:
                        item["participant"].append({
                            "type": [{"text": "not given"}],
                            "individual": {"reference": f"Practitioner/{record[columns.index('participantID')]}"}
                        })
                        participant_added = True

            ###OBSERVATION RULES
            elif table_name == "observation" and column in ["subject", "encounter", "performer"]:
                reference = "Patient" if column == "subject" else (
                    "Encounter" if column == "encounter" else "Practitioner")
                item[column] = [{"reference": f"{reference}/{value}"}] if column == "performer" else {
                    "reference": f"{reference}/{value}"}
            elif table_name == "observation" and column == "code":
                item[column] = { "coding": [{ "code": value }]}
            elif table_name == "observation" and column == "valueQuantity":
                value_unit = record[columns.index("valueUnit")]
                item["valueQuantity"] = {"value": float(value), "unit": value_unit}
            elif table_name == "observation" and column == "interpretation":
                item[column] = [{"text": value}]
            elif table_name == "observation" and column == "note":
                item[column] = [{"text": value}]
            elif table_name == "observation" and column == "bodySite":
                item[column] = {"text": value}
            elif table_name == "observation" and column == "method":
                item[column] = {"text": value}
            elif table_name == "observation" and column == "valueUnit":
                continue  # Skip processing the 'valueUnit' column for Observation table
            elif table_name == "observation" and column == "issued":
                value += "T00:00:00Z"  # Add time component if missing

            ###DIAGNOSTICREPORT RULES
            elif table_name == "diagnosticReport" and column == "subject":
                reference = "Patient"
                item[column] = {"reference": f"{reference}/{value}"}
            elif table_name == "diagnosticReport" and column == "encounter":
                reference = "Encounter"
                item[column] = {"reference": f"{reference}/{value}"}
            elif table_name == "diagnosticReport" and column in ["performer"]:
                reference = "Practitioner"
                item[column] = [{"reference": f"{reference}/{value}"}]
            elif column == "code":
                item[column] = {"coding": [{"code": value}]}
            elif table_name == "diagnosticReport" and column == "result":
                item[column] = [{"reference": f"Observation/{value}"}]



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
        "media": ["id", "status", "subject", "operator", "content"],
        "encounter": ["id", "status", "class", "priority", "type", "subject", "participantID", "participantType", "length", "preAdmissionIdentifier", "destination"], #, "subjectStatus" , "plannedStartDate", "plannedEndDate", "diagnoses" only in R5
        "observation": ["id", "status", "code", "subject", "encounter", "issued", "performer", "valueQuantity", "valueUnit", "interpretation", "note", "bodySite", "method"], # device column is to complicated, would need to implement another table as device is a resource in fhir that needs to be referenced
        "diagnosticReport": ["id", "status", "code", "subject", "encounter", "issued", "performer", "result", "note", "mediaComment", "mediaLink"]
    }

    fhir_json = generate_fhir_json(schema)
    print(json.dumps(fhir_json, indent=2))

    cursor.close()
    connection.close()