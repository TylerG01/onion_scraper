import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import mariadb
from tqdm import tqdm
from db_connection import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

nltk.download('punkt')
nltk.download('stopwords')

def fetch_webpage(url, session):
    response = session.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch the webpage: {response.status_code}")

# Function to clean and tokenize text
def clean_and_tokenize(text):
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens]
    tokens = [word for word in tokens if word.isalpha()]  # Remove punctuation
    tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stopwords
    return tokens

def most_common_words(tokens, num=5):
    counter = Counter(tokens)
    return counter.most_common(num)

def fetch_urls_from_database():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        cursor = conn.cursor()
        # Select rows where common_word_1 through common_word_5 are NULL
        cursor.execute("SELECT id, link FROM silver WHERE common_word_1 IS NULL AND common_word_2 IS NULL AND common_word_3 IS NULL AND common_word_4 IS NULL AND common_word_5 IS NULL")
        urls = cursor.fetchall()
        return urls
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_common_words_in_database(url_id, common_words):
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        cursor = conn.cursor()

        # Prepare the update statement
        update_query = """
            UPDATE silver
            SET common_word_1 = %s, common_word_2 = %s, common_word_3 = %s, common_word_4 = %s, common_word_5 = %s
            WHERE id = %s
        """
        common_word_values = [word for word, count in common_words] + [None] * (5 - len(common_words))
        common_word_values.append(url_id)

        cursor.execute(update_query, common_word_values)

        conn.commit()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
    finally:
        if conn:
            conn.close()

def main(session):
    urls = fetch_urls_from_database()
    total_steps = len(urls) * 5
    with tqdm(total=total_steps) as pbar:
        for url_id, url in urls:
            try:
                webpage_content = fetch_webpage(url, session)
                soup = BeautifulSoup(webpage_content, 'html.parser')
                text = soup.get_text(separator=' ')
                tokens = clean_and_tokenize(text)
                common_words = most_common_words(tokens)
                update_common_words_in_database(url_id, common_words)
                pbar.update(5)
            except Exception as e:
                pbar.update(5)
                print(f"Failed to process URL {url}: {e}")

if __name__ == "__main__":
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    main(session)
