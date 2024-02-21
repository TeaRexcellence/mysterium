import sys
import os
import inquirer
import time
from dotenv import load_dotenv
from requests_retry import retry_request
from docker_logs import check_docker_logs  # Import the function from docker_logs.py

if __name__ == '__main__':
    load_dotenv()
    passphrase = os.getenv('MYSTERIUM_PASSPHRASE')
    proxy_port = "40001"
    base_url = "http://127.0.0.1:4050"
    identities_url = f"{base_url}/identities"
    connection_url = f"{base_url}/connection"
    proposals_url = f"{base_url}/proposals?ip_type=residential"

    response = retry_request(identities_url, 'get')
    data = response.json()
    first_identity_id = data['identities'][0]['id']

    unlock_url = f"{base_url}/identities/{first_identity_id}/unlock"
    unlock_response = retry_request(unlock_url, 'put', json={"passphrase": passphrase}, headers={"Content-Type": "application/json"})
    if unlock_response.status_code != 202:
        print("Failed to unlock identity.")
        sys.exit()

    details_url = f"{identities_url}/{first_identity_id}"
    details_response = retry_request(details_url, 'get')
    details_data = details_response.json()
    if details_data['registration_status'] != "Registered" or details_data['balance'] <= 0:
        print("Identity is not registered or balance is too low.")
        sys.exit()

    proposals_response = retry_request(proposals_url, 'get')
    proposals_data = proposals_response.json()
    providers = [(proposal['provider_id'], proposal['location']['country']) for proposal in proposals_data.get('proposals', []) if 'location' in proposal]
    
    # Organize and order the providers by region alphabetically but put all (US) options at the top.
    us_providers = sorted([f"{provider_id} ({country})" for provider_id, country in providers if country == 'US'])
    other_providers = sorted([f"{provider_id} ({country})" for provider_id, country in providers if country != 'US'])
    choices = us_providers + other_providers

    questions = [
        inquirer.List('choice',
                      message="Select a VPN location to connect to",
                      choices=choices,
                      ),
    ]

    for attempt in range(5):
        try:
            answers = inquirer.prompt(questions)
            provider_id = answers['choice'].split()[0]
            print(f"You selected: {answers['choice']}")
            break
        except Exception as e:
            print(f"Error selecting provider (Attempt {attempt+1}): {e}")
            if attempt == 4:
                print("Failed to select provider after multiple attempts.")
                sys.exit(1)
            time.sleep(2)

    retry_request(connection_url, 'delete')
    print("Any existing connection has been stopped.")

    connection_data = {
        "connect_options": {
            "proxy_port": int(proxy_port)
        },
        "consumer_id": first_identity_id,
        "provider_id": provider_id,
        "service_type": "wireguard"
    }

    print_errors = False
    for attempt in range(3):
        try:
            put_response = retry_request(connection_url, 'put', json=connection_data, headers={"Content-Type": "application/json"})
            print(f"Connection setup request sent to {answers['choice']}.")
            break
        except Exception as e:
            print(f"Error setting up the connection (Attempt {attempt+1}): {e}")
            print_errors = True

<<<<<<< Updated upstream
    check_docker_logs(SHOW_INF=True, SHOW_DBG=True, SHOW_DEBUG=True, SHOW_ERR=True, SHOW_WRN=True, LOG_HISTORY=False, CONCATENATE_WARNINGS=True)
=======
    check_docker_logs(SHOW_INF=True, SHOW_DBG=False, SHOW_DEBUG=True, SHOW_ERR=True, SHOW_WRN=True, LOG_HISTORY=False, CONCATENATE_WARNINGS=True)
>>>>>>> Stashed changes
