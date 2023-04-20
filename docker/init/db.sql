DROP DATABASE IF EXISTS fhir;

CREATE DATABASE fhir;

\c fhir

CREATE TABLE patient (
    id VARCHAR PRIMARY KEY,
    status BOOLEAN,
    name VARCHAR,
    telecom VARCHAR,
    gender VARCHAR,
    birthDate DATE,
    deceased BOOLEAN,
    address VARCHAR,
    maritalStatus VARCHAR,
    multipleBirth BOOLEAN,
    photo BYTEA
);

CREATE TABLE practitioner (
    id VARCHAR PRIMARY KEY,
    status VARCHAR,
    name VARCHAR,
    telecom VARCHAR,
    gender VARCHAR,
    birthDate DATE,
    deceased BOOLEAN,
    address VARCHAR,
    photo BYTEA,
    language VARCHAR
);

CREATE TABLE encounter (
    id VARCHAR PRIMARY KEY,
    status VARCHAR,
    class VARCHAR,
    priority VARCHAR,
    type VARCHAR,
    subject VARCHAR,
    subjectStatus VARCHAR,
    serviceProvider VARCHAR,
    participantType VARCHAR,
    plannedStartDate DATE,
    plannedEndDate DATE,
    length INT,
    diagnoses VARCHAR,
    preAdmissionIdentifier VARCHAR,
    admissionDestination VARCHAR,
    FOREIGN KEY (subject) REFERENCES patient (id),
    FOREIGN KEY (preAdmissionIdentifier) REFERENCES practitioner (id),
    FOREIGN KEY (admissionDestination) REFERENCES practitioner (id)
);

CREATE TABLE encounter_participant (
    encounter_id VARCHAR,
    practitioner_id VARCHAR,
    PRIMARY KEY (encounter_id, practitioner_id),
    FOREIGN KEY (encounter_id) REFERENCES encounter (id),
    FOREIGN KEY (practitioner_id) REFERENCES practitioner (id)
);

CREATE TABLE observation (
    id VARCHAR PRIMARY KEY,
    status VARCHAR,
    code VARCHAR,
    subject VARCHAR,
    encounter VARCHAR,
    issued DATE,
    performer VARCHAR,
    valueQuantity VARCHAR,
    valueString VARCHAR,
    valueBool BOOLEAN,
    valueInteger INT,
    interpretation VARCHAR,
    note VARCHAR,
    bodySite VARCHAR,
    method VARCHAR,
    device VARCHAR,
    FOREIGN KEY (subject) REFERENCES patient (id),
    FOREIGN KEY (encounter) REFERENCES encounter (id),
    FOREIGN KEY (performer) REFERENCES practitioner (id)
);

CREATE TABLE diagnosticreport (
    id VARCHAR PRIMARY KEY,
    status VARCHAR,
    code VARCHAR,
    subject VARCHAR,
    encounter VARCHAR,
    issued DATE,
    performer VARCHAR,
    result VARCHAR,
    note VARCHAR,
    mediaComment VARCHAR,
    mediaLink VARCHAR,
    FOREIGN KEY (subject) REFERENCES patient (id),
    FOREIGN KEY (encounter) REFERENCES encounter (id),
    FOREIGN KEY (performer) REFERENCES practitioner (id)
);