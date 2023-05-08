# FHIRTERMINALNODE

## TESTING ENVIRONMENT

### DOCKER

SOURCEDBPATIENT

The docker dir in this repo contains multiple dirs for different dockerfiles. 
They all work together in the docker-compose.yaml under the docker dir.

The fhirterminalnode_sourcedbpatient container runs a postgresql with a custom schema to
simulate a patients local db. The docker-compose.yaml runs a sql file which builds
the schema and a python script that updates the patients db with synthetic data.

The fhirterminalnode_sourceterminal container is the node that wrapps the data to send it
to any requester. It is based on the dockerfile image under the docker multicorn2 dir.
This image was build up on my forked repo here:

[cmde-lusional/multicorn2
](https://github.com/cmde-lusional/multicorn2)
 
Together fhirterminalnode_sourcedbpatient and fhirterminalnode_sourceterminal work as a "unit". Our test 
environment is build around this units.

A init folder will mount all the necessary scripts into any of the container. The "import_foreign_schema.py" uses 
the docker-compose.yaml env "SOURCE_PORT" to access its units partner. 
Partners for example are:
- fhirterminalnode_sourcedbpatient_0 and fhirterminalnode_sourceterminal_0
- fhirterminalnode_sourcedbpatient_1 and fhirterminalnode_sourceterminal_1
- ...

The "docker-startup.sh" is dynamically creating the docker-compose.yaml. With this script we can scale up
the numbers of our containers inside our docker host to simulate multiple patient instances.

-> you can find more infor inside the LEGACY section of this README.md

```
docker-compose up -d
docker-compose ps
docker-compose logs
docker-compose logs fhirnode_sourcedb_patient
docker-compose down
```



# LEGACY

FHIRBASE

For fhirbase I created my own multicorn2 image. 
It is based on my research on multicorn2 and you can find my results 
and more information here:

[cmde-lusional/multicorn2
](https://github.com/cmde-lusional/multicorn2)

I didn't edit the fhirbase image.

You can run the docker-compose.yaml contained inside the docker directory
in this repository.

It will start two container for simulating the fdw access from a target 
database using multicorn2.4, python 3.7.0 and postgresql 13.3., to a source
database running the open source tool fhirbase. 

I forked the multicorn repository and changed it, so it is running for 
my needs. For example, I fixed it to be able to handle jsonb columns.

docker cmd

```
docker-compose up -d
docker-compose ps
docker-compose logs
docker-compose logs fhirnode_multicorn
docker-compose down
```

The docker storage is persistent, so if you restart the container 
the databases will still exist.

access container cmd

```
docker exec -it <dockerid> /bin/bash
```

CONFIGURATION

fhirbase (source)

```
#cmd
psql

#psql
CREATE DATABASE fb;
\q

#cmd (initiliation of database and loading of synthetic data)
fhirbase -d fb --fhir=3.0.1 init
fhirbase -d fb --fhir=3.0.1 load ./bundle.ndjson.gzip

#testing data access
psql -d fb

SELECT resource->'name', resource->'birthDate'
FROM patient
LIMIT 10;
```

```
CREATE USER fdw_user with encrypted password 'password';
CREATE VIEW restricted_view AS
SELECT * FROM patient
WHERE id = 'd3af67c9-0c02-45f2-bc91-fea45af3ee83';
GRANT SELECT ON restricted_view TO fdw_user;
```

fhirnode_multicorn (target)

First you need to create a missing data type from the source database 
inside the target database. Without you are not able to import the schema.
```
CREATE TYPE resource_status AS ENUM (
	'created', 'updated', 'deleted', 'recreated'
);
```

Then you can use multicorn.
```
CREATE EXTENSION multicorn;
CREATE SERVER alchemy_srv foreign data wrapper multicorn OPTIONS ( wrapper 'multicorn.sqlalchemyfdw.SqlAlchemyFdw' , db_url 'postgresql://fdw_user:password@ip/db' );
IMPORT FOREIGN SCHEMA public LIMIT TO ( restricted_view ) FROM SERVER alchemy_srv INTO public;
SELECT * FROM restricted_view;
```