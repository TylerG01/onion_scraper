import mariadb
from db_connection import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

def connect_to_db():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None
# Main function to delete duplicate rows
def delete_duplicate_rows():
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        # SQL query to delete duplicate rows
        delete_query = """
        DELETE t1
        FROM raw t1
        JOIN (
            SELECT link, MIN(id) as min_id
            FROM raw
            GROUP BY link
            HAVING COUNT(*) > 1
        ) t2 ON t1.link = t2.link AND t1.id > t2.min_id;
        """
        cursor.execute(delete_query)
        conn.commit()

    except mariadb.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        conn.close()
        print("Finished removing duplicates.")

if __name__ == "__main__":
    delete_duplicate_rows()
