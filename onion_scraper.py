import requests
import db_construction
import seeder
import duplicates
import onion_ping_v2
import content_check
import b2s
import common_words

def configure_socks_proxy():
    socks_proxy = 'socks5h://127.0.0.1:9050'
    proxies = {
        'http': socks_proxy,
        'https': socks_proxy
    } 
    # Create a global requests session with the proxy configuration
    session = requests.Session()
    session.proxies.update(proxies)
    return session

def get_raw_table_row_count():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM raw")
        row_count = cur.fetchone()[0]
        conn.close()
        return row_count
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return 0

def run_initial_setup():
    db_construction_input = input("Would you like to execute db_construction.py? (yes/no): ").strip().lower()
    run_db_construction = db_construction_input == 'yes'
    
    seeder_input = input("Would you like to execute seederV2.py? (yes/no): ").strip().lower()
    run_seeder = seeder_input == 'yes'
    if run_db_construction:
        db_construction.main()
    if run_seeder:
        seederV2.main()
    return run_db_construction, run_seeder

def run_modules_in_order(session, row_limit):
    duplicatesV2.delete_duplicate_rows()
    duplicatesV2.non_onion()
    onion_ping_v2.main(session, row_limit)
    content_check.main(session)
    b2sV2.move_all_rows()
    common_words.main(session)

if __name__ == "__main__":
    try:
        session = configure_socks_proxy()
        run_db_construction, run_seeder = run_initial_setup()
        row_limit = 12  # Example predefined value, change as needed
        while get_raw_table_row_count() > 1:
            run_modules_in_order(session, row_limit)
    
    except Exception as e:
        print(f"An error occurred: {e}")
