import mariadb
from mariadb import Error
from db_connection import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

# Define SQL queries to create tables
create_raw_table_query = """
CREATE TABLE IF NOT EXISTS raw (
    id INT AUTO_INCREMENT PRIMARY KEY,
    link VARCHAR(255) NOT NULL,
    phrase VARCHAR(255),
    status VARCHAR(255),
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_bronze_table_query = """
CREATE TABLE IF NOT EXISTS bronze (
    id INT AUTO_INCREMENT PRIMARY KEY,
    raw_id INT,
    link VARCHAR(255),
    phrase VARCHAR(255),
    status VARCHAR(255),
    time TIMESTAMP,
    data VARCHAR(255),
    FOREIGN KEY (raw_id) REFERENCES raw(id)
);
"""

create_silver_table_query = """
CREATE TABLE IF NOT EXISTS silver (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bronze_id INT,
    link VARCHAR(255),
    phrase VARCHAR(255),
    status VARCHAR(255),
    time TIMESTAMP,
    refined_data VARCHAR(255),
    images TEXT,
    Ext_Links TEXT,
    FOREIGN KEY (bronze_id) REFERENCES bronze(id)
);
"""

external_link_columns = ",\n".join([f"External_Link_{i} TEXT" for i in range(1, 51)])

create_gold_table_query = f"""
CREATE TABLE IF NOT EXISTS gold (
    id INT AUTO_INCREMENT PRIMARY KEY,
    silver_id INT,
    link VARCHAR(255),
    phrase VARCHAR(255),
    status VARCHAR(255),
    time TIMESTAMP,
    final_data VARCHAR(255),
    images TEXT,
    Ext_Links TEXT,
    Service_Type VARCHAR(255),
    common_word_1 VARCHAR(255),
    common_word_2 VARCHAR(255),
    common_word_3 VARCHAR(255),
    common_word_4 VARCHAR(255),
    {external_link_columns},
    FOREIGN KEY (silver_id) REFERENCES silver(id)
);
"""
# Function to create tables
def create_tables(cursor):
    tables = {
        "raw": create_raw_table_query,
        "bronze": create_bronze_table_query,
        "silver": create_silver_table_query,
        "gold": create_gold_table_query
    }
    
    for table_name, create_table_query in tables.items():
        try:
            print(f"Creating table {table_name}...")
            cursor.execute(create_table_query)
            print(f"Table {table_name} created successfully.")
        except mariadb.Error as err:
            if err.errno == 1050:  # Error code for table already exists
                print(f"Table {table_name} already exists.")
            else:
                print(f"Error creating table {table_name}: {err}")

# Main function to connect to the database and create tables
def main():
    try:
        db_connection = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        cursor = db_connection.cursor()

        create_tables(cursor)

        db_connection.commit()

        cursor.close()
        db_connection.close()
        print("Database connection closed.")
        
    except mariadb.Error as err:
        print(f"Error: {err}")
        if err.errno == 1045:  # Error code for access denied
            print("Something is wrong with your user name or password")
        elif err.errno == 1049:  # Error code for unknown database
            print("Database does not exist")
        else:
            print(err)

if __name__ == "__main__":
    main()
