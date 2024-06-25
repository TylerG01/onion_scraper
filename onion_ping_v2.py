import mariadb
import requests
from datetime import datetime
from requests.exceptions import RequestException
from db_connection import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

# Function to process URLs and insert into bronze table with error handling
def process_urls_and_insert(connection, session, url, phrase):
    try:
        # Prepend "http://" to the URL if it doesn't already start with it
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        # Fetch URL using session
        response = session.get(url)
        status_code = response.status_code
        # URL returned HTTP status code 200, insert into bronze table
        if status_code == 200:
            insert_query = "INSERT INTO bronze (link, phrase, status, time) VALUES (%s, %s, %s, %s)"
            data = (url, phrase, status_code, datetime.now())
            cursor = connection.cursor()
            cursor.execute(insert_query, data)
            connection.commit()
            cursor.close()
            print(f"Inserted URL {url} into bronze table")
        # Update status to 408 (Request Timeout) in raw for failed URL
        else:
            update_query = "UPDATE raw SET status = %s WHERE link = %s"
            cursor = connection.cursor()
            cursor.execute(update_query, (408, url))
            connection.commit()
            cursor.close()
            print(f"Updated status for URL {url} in raw to 408")
    # Update status to 408 (Request Timeout) in raw for failed URL
    except RequestException as e:
        update_query = "UPDATE raw SET status = %s WHERE link = %s"
        cursor = connection.cursor()
        cursor.execute(update_query, (408, url))
        connection.commit()
        cursor.close()
        print(f"Error fetching URL {url}: {str(e)}")

# Function to fetch URLs
def fetch_and_process_urls(connection, session):
    cursor = connection.cursor()
    
    try:
        # Query URLs and phrases from the "raw" table in the database
        query = "SELECT link, phrase FROM raw"
        cursor.execute(query)
        rows = cursor.fetchall()
        # Process each URL using provided session
        for (url, phrase) in rows:
            process_urls_and_insert(connection, session, url, phrase)
    except mariadb.Error as e:
        print(f"Error accessing database: {str(e)}")
    finally:
        cursor.close()

# Main function to be executed
def main(session):
    try:
        db_connection = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        fetch_and_process_urls(db_connection, session)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {str(e)}")
    # Close database connection
    finally:
        if db_connection:
            db_connection.close()

# If this script is run directly, execute the main function with a default session
if __name__ == "__main__":
    # Create a requests session with SOCKS proxy configuration
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    # Execute main function with the created session
    main(session)
