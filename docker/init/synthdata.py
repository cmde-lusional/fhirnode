from faker import Faker
import random
import uuid
import psycopg2
from psycopg2 import sql
import argparse

parser = argparse.ArgumentParser(description='Connect to PostgreSQL database.')

parser.add_argument('-u', '--user', help='PostgreSQL username', required=True)
parser.add_argument('-p', '--password', help='PostgreSQL password', required=True)

args = parser.parse_args()  # Add this line to parse the arguments

# Connect to your PostgreSQL database
connection = psycopg2.connect(
    dbname="fhir",
    user=args.user,
    password=args.password,
    host="localhost",
    port="5432"
)
cursor = connection.cursor()

fake = Faker()

# Generate and insert data
num_patients = 1
num_practitioners = 5
num_encounters_per_patient = 5
num_observations_per_encounter = 5
num_diagnosticreports_per_encounter = 3

# Generate a pool of practitioner IDs
practitioner_ids = [str(uuid.uuid4()) for _ in range(num_practitioners)]
practioner_ids_for_encounter = practitioner_ids.copy()

# Generate a single patient
def generate_patient():
    return {
        'id': str(uuid.uuid4()),
        'active': random.choice([True, False]),
        'name': fake.name(),
        'telecom': fake.phone_number(),
        'gender': random.choice(['male', 'female']),
        'birthDate': fake.date_between(start_date='-100y', end_date='today'),
        'deceasedBoolean': random.choice([True, False]),
        'address': fake.address(),
        'maritalStatus': random.choice(['single', 'married', 'divorced']),
        'multipleBirthBoolean': random.choice([True, False]),
        'photo': None  # Assuming you don't need a photo for this example
    }

# Generate a single practitioner
def generate_practitioner():
    return {
        'id': practitioner_ids.pop(),
        'active': random.choice([True, False]),
        'name': fake.name(),
        'telecom': fake.phone_number(),
        'gender': random.choice(['male', 'female']),
        'birthDate': fake.date_between(start_date='-100y', end_date='today'),
        # 'deceasedBoolean': random.choice([True, False]), only in R5
        'address': fake.address(),
        'photo': None,  # Assuming you don't need a photo for this example
        'language': random.choice(['en', 'es', 'fr', 'de', 'it'])
    }

# Generate a single encounter
def generate_encounter(patient_id, practitioner_id):
    if not practioner_ids_for_encounter:
        raise ValueError("No practitioners available for encounter")
    return {
        'id': str(uuid.uuid4()),
        'status': random.choice(['planned', 'arrived', 'in-progress', 'onleave', 'finished', 'cancelled']),
        'class': random.choice(['inpatient', 'outpatient']),
        'priority': random.choice(['high', 'medium', 'low']),
        'type': random.choice(['emergency', 'urgent', 'elective', 'routine']),
        'subject': patient_id,
         #'subjectStatus': random.choice(['active', 'inactive']), only in R5
        'serviceProvider': fake.company(),
        'participantID': random.choice(practioner_ids_for_encounter),
        'participantType': random.choice(['practitioner', 'relatedPerson']),
        'plannedStartDate': fake.date_this_year(),
        'plannedEndDate': fake.date_this_year(),
        'length': random.randint(1, 20),
        'diagnoses': fake.bs(),
        'preAdmissionIdentifier': practitioner_id,
        'admissionDestination': practitioner_id
    }

# Generate a single observation
def generate_observation(patient_id, encounter_id, practitioner_id):
    return {
        'id': str(uuid.uuid4()),
        'status': random.choice(['registered', 'preliminary', 'final', 'amended', 'cancelled', 'entered-in-error']),
        'code': random.choice(['body height', 'body weight', 'blood pressure', 'heart rate']),
        'subject': patient_id,
        'encounter': encounter_id,
        'issued': fake.date_this_year(),
        'performer': practitioner_id,
        'valueQuantity': None,
        'valueString': "{:.2f}".format(random.uniform(1.5, 2)),
        'valueBool': None,
        'valueInteger': None,
        'interpretation': random.choice(['normal', 'abnormal', 'high', 'low']),
        'note': fake.sentence(),
        'bodySite': None,
        'method': 'measurement',
        'device': random.choice(['stadiometer', 'scale', 'sphygmomanometer', 'pulse oximeter'])
    }

def generate_diagnosticreport(patient_id, encounter_id, practitioner_id):
    return {
        'id': str(uuid.uuid4()),
        'status': random.choice(['registered', 'preliminary', 'final', 'amended', 'cancelled', 'entered-in-error']),
        'code': random.choice(['x-ray', 'ultrasound', 'CT scan', 'MRI']),
        'subject': patient_id,
        'encounter': encounter_id,
        'issued': fake.date_this_year(),
        'performer': practitioner_id,
        'result': fake.sentence(),
        'note': fake.sentence(),
        'mediaComment': fake.sentence(),
        'mediaLink': fake.url()
    }

# Function to insert a single patient
def insert_patient(patient):
    query = sql.SQL(
        "INSERT INTO patient (id, active, name, telecom, gender, birthDate, deceasedBoolean, address, maritalStatus, multipleBirthBoolean, photo) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(patient.values()))
    connection.commit()

# Function to insert a single practitioner
def insert_practitioner(practitioner):
    query = sql.SQL(
        "INSERT INTO practitioner (id, active, name, telecom, gender, birthDate, address, photo, language) " #deceasedBoolean only in R5
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(practitioner.values()))
    connection.commit()

# Function to insert a single encounter
def insert_encounter(encounter):
    query = sql.SQL(
        "INSERT INTO encounter (id, status, class, priority, type, subject, serviceProvider, participantID, participantType, plannedStartDate, plannedEndDate, length, diagnoses, preAdmissionIdentifier, admissionDestination) " #subjectStatus only in R5
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(encounter.values()))
    connection.commit()

# Function to insert a single observation
def insert_observation(observation):
    query = sql.SQL(
        "INSERT INTO observation (id, status, code, subject, encounter, issued, performer, valueQuantity, valueString, valueBool, valueInteger, interpretation, note, bodySite, method, device) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(observation.values()))
    connection.commit()

# Function to insert a single diagnosticreport
def insert_diagnosticreport(diagnosticreport):
    query = sql.SQL(
        "INSERT INTO diagnosticreport (id, status, code, subject, encounter, issued, performer, result, note, mediaComment, mediaLink) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(diagnosticreport.values()))
    connection.commit()

practitioners = [generate_practitioner() for _ in range(num_practitioners)]
for practitioner in practitioners:
    insert_practitioner(practitioner)

patients = [generate_patient() for _ in range(num_patients)]
for patient in patients:
    insert_patient(patient)
    for _ in range(num_encounters_per_patient):
        encounter = generate_encounter(patient['id'], random.choice(practitioners)['id'])
        insert_encounter(encounter)

        for _ in range(num_observations_per_encounter):
            observation = generate_observation(patient['id'], encounter['id'], random.choice(practitioners)['id'])
            insert_observation(observation)

        for _ in range(num_diagnosticreports_per_encounter):
            diagnosticreport = generate_diagnosticreport(patient['id'], encounter['id'],
                                                         random.choice(practitioners)['id'])
            insert_diagnosticreport(diagnosticreport)

# Close the connection after inserting data
cursor.close()
connection.close()
