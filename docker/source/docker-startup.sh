#!/bin/bash

# Save the original docker-compose.yaml file
cp docker-compose.yaml docker-compose_original.yaml

# Clear the services section
echo "version: '3.8'" > docker-compose.yaml
echo "services:" >> docker-compose.yaml

for i in {0..10}
do
  sourcedbpatient_port=$((5433 + (2 * i)))
  sourceterminalnode_port=$((5434 + (2 * i)))
  sourceterminalnode_flask_port=$((5000 + i))

  cat <<EOT >> docker-compose.yaml
  fhirterminalnode_sourcedbpatient_${i}:
    image: sourcedbpatient
    container_name: fhirterminalnode_sourcedbpatient_${i}
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fhir
    ports:
      - "${sourcedbpatient_port}:5432"
    volumes:
      - fhirterminalnode_sourcedbpatient_data_${i}:/var/lib/postgresql/data
      - ./init:/init
      - ./init/images:/app/images
    command: ["bash", "-c", "docker-entrypoint.sh postgres & sleep 30 && psql -U postgres -f /init/db.sql && python3 /init/synthdata.py -u postgres -p password && tail -f /dev/null"]

  fhirterminalnode_sourceterminalnode_${i}:
    image: fhirnode_multicorn
    container_name: fhirterminalnode_sourceterminalnode_${i}
    depends_on:
      - fhirterminalnode_sourcedbpatient_${i}
    environment:
      - POSTGRES_PASSWORD=password
      - SOURCE_PORT=${sourcedbpatient_port}
    ports:
      - "${sourceterminalnode_port}:5432"
      - "${sourceterminalnode_flask_port}:5000"
    volumes:
      - fhirterminalnode_sourceterminalnode_data_${i}:/var/lib/postgresql/data
      - ./init:/init
    command: ["bash", "-c", "docker-entrypoint.sh postgres & sleep 5 && tail -f /dev/null"]

EOT
done

echo "volumes:" >> docker-compose.yaml
for i in {0..10}
do
  echo "  fhirterminalnode_sourcedbpatient_data_${i}:" >> docker-compose.yaml
  echo "  fhirterminalnode_sourceterminalnode_data_${i}:" >> docker-compose.yaml
done

# Start the services
docker-compose up -d



