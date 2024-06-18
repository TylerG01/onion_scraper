import requests
import db_construction
import seeder
import duplicates
import onion_ping_v2

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

def run_modules_in_order(session):
    db_construction.main()
    seeder.main()
    duplicates.remove_duplicate_rows()
    onion_ping_v2.main(session)

if __name__ == "__main__":
    session = configure_socks_proxy()
    run_modules_in_order(session)
