DROP DATABASE IF EXISTS fhir;

CREATE DATABASE fhir;

\c fhir

CREATE TABLE patient (
    id VARCHAR PRIMARY KEY,
    active BOOLEAN,
    name VARCHAR,
    telecom VARCHAR,
    gender VARCHAR,
    birthDate DATE,
    deceasedBoolean BOOLEAN,
    address VARCHAR,
    maritalStatus VARCHAR,
    multipleBirthBoolean BOOLEAN,
    photo BYTEA
);

CREATE TABLE practitioner (
    id VARCHAR PRIMARY KEY,
    active BOOLEAN,
    name VARCHAR,
    telecom VARCHAR,
    gender VARCHAR,
    birthDate DATE,
    --deceasedBoolean BOOLEAN, only in R5
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
    -- subjectStatus VARCHAR, only in R5
    -- serviceProvider VARCHAR, relation to complicated because I need to also create that organization - should create another table
    participantID VARCHAR,
    participantType VARCHAR,
    -- plannedStartDate DATE,only in R5
    -- plannedEndDate DATE, only in R5
    length INT,
    -- diagnoses VARCHAR, only in R5
    preAdmissionIdentifier VARCHAR,
    destination VARCHAR,
    FOREIGN KEY (subject) REFERENCES patient (id),
    FOREIGN KEY (participantID) REFERENCES practitioner (id),
    FOREIGN KEY (preAdmissionIdentifier) REFERENCES practitioner (id),
    FOREIGN KEY (destination) REFERENCES practitioner (id)
);

--CREATE TABLE encounter_participant (
--    encounter_id VARCHAR,
--    practitioner_id VARCHAR,
--    PRIMARY KEY (encounter_id, practitioner_id),
--    FOREIGN KEY (encounter_id) REFERENCES encounter (id),
--    FOREIGN KEY (practitioner_id) REFERENCES practitioner (id)
--);

CREATE TABLE observation (
    id VARCHAR PRIMARY KEY,
    status VARCHAR,
    code VARCHAR,
    subject VARCHAR,
    encounter VARCHAR,
    issued DATE,
    performer VARCHAR,
    valueQuantity VARCHAR,
    valueUnit VARCHAR,
    interpretation VARCHAR,
    note VARCHAR,
    bodySite VARCHAR,
    method VARCHAR,
    --- device VARCHAR, to complicated, would need to implement another table as device is a resource in fhir that needs to be referenced
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