import os
import requests
from bs4 import BeautifulSoup
import datetime
import re
import time
import mariadb
from db_connection import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

def main():
    start_time = time.time()
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Define the path to the words_list.txt file
    file_path = '/absolute/path/to/words.txt'/words_list.txt'
    with open(file_path, 'r') as file:
        user_list = [line.strip() for line in file if line.strip()]

    try:
        db_connection = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        cursor = db_connection.cursor()

        # Iterate through the list using a for loop
        for item in user_list:
            if " " in item:
                item_formatted = item.replace(" ", "+")
            else:
                item_formatted = item
            
            target_url = "https://ahmia.fi/search/?q=" + item_formatted
            print(target_url)
            response = requests.get(target_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            anchor_tags = soup.find_all('a')
            url_list = [tag.get('href') for tag in anchor_tags if tag.get('href')]
            onion_pattern = re.compile(r'\w+\.onion')
            url_list = [re.search(onion_pattern, url).group() for url in url_list if re.search(onion_pattern, url)]

            for url in url_list:
                insert_query = "INSERT INTO raw (link, phrase, status) VALUES (?, ?, ?)"
                insert_values = (url, item, 'unknown')
                cursor.execute(insert_query, insert_values)
            
            db_connection.commit()
            print(f"Total .onion URLs scraped for '{item}': {len(url_list)}")

        print("Data successfully inserted into the database!")

    except mariadb.Error as error:
        print(f"Error: {error}")

    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()
            print("Database db_connection closed.")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Script execution time: {execution_time} seconds")

if __name__ == "__main__":
    main()

