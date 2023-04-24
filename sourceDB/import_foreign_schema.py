import psycopg2
import urllib.parse

source_info = {
    "dbname": "fhir",
    "user": "postgres",
    "password": "password",
    "ip": "192.168.209.1"
}

# Construct the DB URL string using the source_info dictionary
db_url_target = f"postgresql://{source_info['user']}:{source_info['password']}@{source_info['ip']}/{source_info['dbname']}"

# URL encode the DB URL string
db_url_encoded = urllib.parse.quote_plus(db_url_target)

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

    # Commit the changes and close the cursor
    target_conn.commit()
    target_cur.close()

# Target database connection
target_conn = psycopg2.connect(
    dbname="fhir",
    user="postgres",
    password="password",
    host="localhost",
    port="5430"
)

# Create the Multicorn extension and foreign server
target_cur = target_conn.cursor()
target_cur.execute("CREATE EXTENSION IF NOT EXISTS multicorn;")
# Use the encoded DB URL string in the SQL query
target_cur.execute(f"""
    CREATE DATABASE IF NOT EXISTS {source_info['dbname']};
    \c {source_info['dbname']}
    CREATE SERVER IF NOT EXISTS alchemy_srv;
    FOREIGN DATA WRAPPER multicorn
    OPTIONS (
        wrapper 'multicorn.sqlalchemyfdw.SqlAlchemyFdw',
        db_url '{db_url_encoded}'
    );
""")
target_conn.commit()
target_cur.close()

# List of table names
table_names = ['table1', 'table2', 'table3']

# Import foreign schema for the given table names
import_foreign_schema(target_conn, table_names)

# Close the target connection
target_conn.close()
