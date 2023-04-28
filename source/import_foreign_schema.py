import psycopg2
import urllib.parse
import socket
import socket

#host_ip = socket.gethostbyname('docker.for.mac.localhost')
host_ip = socket.gethostbyname('host.docker.internal')
print("Docker Host IP Address:", host_ip)

source_info = {
    "dbname": "fhir",
    "user": "postgres",
    "password": "password",
    "ip": host_ip,
    "port": "5432",
    "port_docker": "5431"
}

target_info = {
    "dbname": "fhir",
    "user": "postgres",
    "password": "password",
    "ip": "localhost",
    "port": "5432",
    "port_docker": "5430",
}

# Construct the DB URL string using the source_info dictionary
db_url_target = f"""postgresql://{source_info['user']}:{source_info['password']}@{source_info['ip']}:{source_info['port_docker']}/{source_info['dbname']}"""

# URL encode the DB URL string
# db_url_encoded = urllib.parse.quote_plus(db_url_target)

def create_database():
    conn = psycopg2.connect(
        user=target_info['user'],
        password=target_info['password'],
        host=target_info['ip'],
        port=target_info['port']
    )

    cursor = conn.cursor()
    conn.autocommit = True

    # Check if database fhir exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{target_info['dbname']}'")
    exists = cursor.fetchone()

    # Create the 'fhir' database if it doesn't already exist
    if not exists:
        create_cmd = f"CREATE DATABASE {source_info['dbname']}"
        #  grant_cmd = sql.SQL('GRANT ALL PRIVILEGES ON DATABASE {} TO dbuser').format(dbname)
        cursor.execute(create_cmd)
        # cursor.execute(grant_cmd)

    cursor.close()
    conn.close()

# Function to import foreign schema for a list of table names
def import_foreign_schema(target_conn, table_names):
    target_cur = target_conn.cursor()

    # Loop over the table names
    for table_name in table_names:
        # Import foreign schema for each table
        query = f"""
            IMPORT FOREIGN SCHEMA public
            LIMIT TO ({table_name})
            FROM SERVER alchemy_srv
            INTO public;
        """
        target_cur.execute(query)


create_database()


# Target database connection
target_conn = psycopg2.connect(
    dbname=target_info['dbname'],
    user=target_info['user'],
    password=target_info['password'],
    host=target_info['ip'],
    port=target_info['port']
)

"""# Create the Multicorn extension and foreign server
target_cur = target_conn.cursor()
target_cur.execute("CREATE EXTENSION IF NOT EXISTS multicorn;")
"""

target_cur = target_conn.cursor()
# Use the encoded DB URL string in the SQL query
target_cur.execute(f"""
    DROP SERVER alchemy_srv CASCADE;
    CREATE EXTENSION IF NOT EXISTS multicorn;
    CREATE SERVER IF NOT EXISTS alchemy_srv
    FOREIGN DATA WRAPPER multicorn
    OPTIONS (
        wrapper 'multicorn.sqlalchemyfdw.SqlAlchemyFdw',
        db_url '{db_url_target}'
    )
""")

#db_url 'postgresql://fdw_user:password@192.168.1.102:5431/fhir'

# List of table names
table_names = ['patient', 'practitioner', 'media', 'encounter', 'observation', 'diagnosticReport'] #, 'encounter_participant'

# Import foreign schema for the given table names
import_foreign_schema(target_conn, table_names)

# Commit the changes and close the cursor and connection
target_conn.commit()
# Close the target connection
target_conn.close()
