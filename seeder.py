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

    user_list = ["bitcoin", "gift cards", "crypto", "untraceable", "phone", "email"]

    # Establish database db_connection
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
            # Send a GET request to the target URL
            response = requests.get(target_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all the anchor tags (links) on the page
            anchor_tags = soup.find_all('a')
            # Create a list to save the URLs
            url_list = [tag.get('href') for tag in anchor_tags if tag.get('href')]
            # Remove URLs that don't match the pattern \w+\.onion using regular expressions
            onion_pattern = re.compile(r'\w+\.onion')
            url_list = [re.search(onion_pattern, url).group() for url in url_list if re.search(onion_pattern, url)]

            # Insert the URLs into the database
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
