import mariadb
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
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

def fetch_links(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, link FROM bronze")
    return cursor.fetchall()

def count_rows(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bronze")
    return cursor.fetchone()[0]

def check_site(url, session=None):
    try:
        if session:
            response = session.get(url)
        else:
            response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        img_extensions = ['.jpeg', '.jpg', '.gif', '.png', '.pdf', '.webp']
        images = soup.find_all('img')
        for ext in img_extensions:
            images.extend(soup.find_all(src=lambda x: x and x.endswith(ext)))

        external_links = [a['href'] for a in soup.find_all('a', href=True) if not a['href'].startswith('#') and 'http' in a['href']]

        has_images = bool(images)
        has_external_links = bool(external_links)

        return has_images, has_external_links
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None

def update_database(conn, url_id, has_images, has_external_links):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bronze SET images = ?, Ext_Links = ? WHERE id = ?",
        (has_images, has_external_links, url_id)
    )
    conn.commit()

def main(session=None):
    conn = connect_to_db()
    if conn is None:
        return

    total_rows = count_rows(conn)
    links = fetch_links(conn)

    with tqdm(total=total_rows, desc="Processing URLs", unit="URL") as pbar:
        for url_id, link in links:
            has_images, has_external_links = check_site(link, session=session)
            if has_images is not None and has_external_links is not None:
                update_database(conn, url_id, has_images, has_external_links)
            pbar.update(1)

    conn.close()
    print("Finished executing the script.")

if __name__ == "__main__":
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    main(session=session)
