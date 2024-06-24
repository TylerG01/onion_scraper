import mariadb
from db_connection import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

def remove_duplicate_rows():
    total_deleted = 0
    try:
        # Connect to your MariaDB database
        db_connection = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        
        while True:
            cursor = db_connection.cursor()
            query = """
                SELECT link, COUNT(*)
                FROM raw
                GROUP BY link
                HAVING COUNT(*) > 1
            """
            cursor.execute(query)
            duplicate_rows = cursor.fetchall()

            # Flag to track if any rows were deleted in this iteration
            rows_deleted = False

            # Iterate through duplicate rows and delete duplicates
            for row in duplicate_rows:
                link = row[1]
                
                # SQL query to delete all but one row per duplicate link (keep the one with the smallest id)
                delete_query = """
                    DELETE FROM raw
                    WHERE link = %s
                    ORDER BY link DESC  # Optional: Delete latest row based on link
                    LIMIT 1  # Delete only one row per duplicate link
                """
                cursor.execute(delete_query, (link,))
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    print(f"Deleted {deleted_count} row(s) for duplicate link '{link}'")
                    total_deleted += deleted_count  # Increment total deleted count
                    rows_deleted = True  # Set flag to True if rows were deleted

            # Commit changes to the database
            db_connection.commit()
            cursor.close()
            # If no rows were deleted in this iteration, break out of the loop
            if not rows_deleted:
                break

        print("No more duplicates to delete. Script completed.")
        print(f"Total number of items deleted: {total_deleted}")

    except mariadb.Error as error:
        print(f"Error: {error}")
    # Close database connection
    finally:
        if 'db_connection' in locals() and db_connection is not None:
            db_connection.close()
            print("Database connection closed.")

# Call the function to remove duplicate rows continuously
remove_duplicate_rows()
