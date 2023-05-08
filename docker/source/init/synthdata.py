from faker import Faker
import random
import uuid
import psycopg2
from psycopg2 import sql
import argparse
import base64
import os

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
practioner_ids_for_relation = practitioner_ids.copy()

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

# Generate a single media
def generate_media(patient_id, practitioner_id):
    image_folder = "/app/images"
    image_files = os.listdir(image_folder)
    random_image_file = random.choice(image_files)
    image_path = os.path.join(image_folder, random_image_file)
    #Fix for kubernetes: image_path = os.path.realpath(os.path.join(image_folder, random_image_file))

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    return {
        'id': str(uuid.uuid4()),
        'status': random.choice(['preparation', 'in-progress', 'not-done', 'on-hold', 'stopped', 'completed', 'entered-in-error', 'unknown']),
        'subject': patient_id,
        'operator': practitioner_id,
        'content': encoded_image
    }

# Generate a single encounter
def generate_encounter(patient_id, practitioner_id):
    if not practioner_ids_for_relation:
        raise ValueError("No practitioners available for encounter")
    return {
        'id': str(uuid.uuid4()),
        'status': random.choice(['planned', 'arrived', 'in-progress', 'onleave', 'finished', 'cancelled']),
        'class': random.choice(['inpatient', 'outpatient']),
        'priority': random.choice(['high', 'medium', 'low']),
        'type': random.choice(['emergency', 'urgent', 'elective', 'routine']),
        'subject': patient_id,
         #'subjectStatus': random.choice(['active', 'inactive']), only in R5
         # 'serviceProvider': fake.company(), relation to complicated because I need to also create that organization - should create another table
        'participantID': random.choice(practioner_ids_for_relation),
        'participantType': random.choice(['practitioner', 'relatedPerson']),
         # 'plannedStartDate': fake.date_this_year(), only in R5
         # 'plannedEndDate': fake.date_this_year(), only in R5
        'length': random.randint(1, 20),
         # 'diagnoses': fake.bs(), only in R5
        'preAdmissionIdentifier': practitioner_id,
        'destination': practitioner_id
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
        'valueQuantity': "{:.2f}".format(random.uniform(1.5, 2)),
        'valueUnit': random.choice(['meter', 'kg', 'mmHg']),
        'interpretation': random.choice(['normal', 'abnormal', 'high', 'low']),
        'note': fake.sentence(),
        'bodySite': random.choice(['left', 'right', 'front', 'back', 'head']),
        'method': 'measurement',
         # 'device': random.choice(['stadiometer', 'scale', 'sphygmomanometer', 'pulse oximeter']) to complicated, would need to implement another table as device is a resource in fhir that needs to be referenced
    }

# Generate a single diagnostic report
def generate_diagnosticreport(patient_id, encounter_id, practitioner_id, observation_id, media_id):
    return {
        'id': str(uuid.uuid4()),
        'status': random.choice(['registered', 'preliminary', 'final', 'amended', 'cancelled', 'entered-in-error']),
        'code': random.choice(['1-8', '10002-4', '10010-7']),
        'subject': patient_id,
        'encounter': encounter_id,
        'issued': fake.date_this_year(),
        'performer': practitioner_id,
        'result': observation_id,
        # 'note': fake.sentence(), only in R5
        'mediaComment': fake.sentence(),
        'mediaLink': media_id  # Change this line to use the media_id parameter
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

# Function to insert a single media
def insert_media(media):
    query = sql.SQL(
        "INSERT INTO media (id, status, subject, operator, content) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(media.values()))
    connection.commit()

# Function to insert a single encounter
def insert_encounter(encounter):
    query = sql.SQL(
        "INSERT INTO encounter (id, status, class, priority, type, subject, participantID, participantType, length, preAdmissionIdentifier, destination) " #subjectStatus , plannedStartDate, plannedEndDate, diagnoses only in R5; , serviceProvider to complicated
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(encounter.values()))
    connection.commit()

# Function to insert a single observation
def insert_observation(observation):
    query = sql.SQL(
        "INSERT INTO observation (id, status, code, subject, encounter, issued, performer, valueQuantity, valueUnit, interpretation, note, bodySite, method) " # , device - to complicated, would need to implement another table as device is a resource in fhir that needs to be referenced
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, list(observation.values()))
    connection.commit()

# Function to insert a single diagnosticReport
def insert_diagnosticreport(diagnosticreport):
    query = sql.SQL(
        "INSERT INTO diagnosticReport (id, status, code, subject, encounter, issued, performer, result, mediaComment, mediaLink) " #, note only in R5
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
            observation_id = str(uuid.uuid4())
            observation['id'] = observation_id
            insert_observation(observation)

            for _ in range(num_diagnosticreports_per_encounter):
                media = generate_media(patient['id'], random.choice(practitioners)['id'])
                media_id = media['id']
                insert_media(media)

                diagnosticreport = generate_diagnosticreport(patient['id'], encounter['id'],
                                                             random.choice(practitioners)['id'], observation_id,
                                                             media_id)
                insert_diagnosticreport(diagnosticreport)

# Close the connection after inserting data
cursor.close()
connection.close()
