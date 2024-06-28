import mariadb
from db_connection import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

def move_rows_with_ones():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        cursor = conn.cursor()
        # Query to select rows with '1' in 'images' or 'Ext_Links' columns from 'bronze' table
        select_query = """
        SELECT * FROM bronze WHERE images = '1' OR Ext_Links = '1'
        """
        cursor.execute(select_query)
        rows_to_move = cursor.fetchall()

        # Check if there are rows to move
        if not rows_to_move:
            print("No rows to move.")
            return

        columns = [desc[0] for desc in cursor.description if desc[0] != 'raw_id']
        insert_query = f"INSERT INTO silver ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        rows_to_insert = [tuple(row[idx] for idx, col in enumerate(cursor.description) if col[0] != 'raw_id') for row in rows_to_move]
        cursor.executemany(insert_query, rows_to_insert)
        rows_inserted_count = cursor.rowcount
        delete_query = "DELETE FROM bronze WHERE images = '1' OR Ext_Links = '1'"
        cursor.execute(delete_query)
        rows_deleted_count = cursor.rowcount
        conn.commit()
        print(f"Moved {rows_inserted_count} rows from 'bronze' to 'silver'.")

    except mariadb.Error as e:
        print(f"Error: {e}")
    finally:

        if conn:
            conn.close()

if __name__ == "__main__":
    move_rows_with_ones()
