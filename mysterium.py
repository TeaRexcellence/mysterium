import requests
import sys
import os
import inquirer
import time
import subprocess
import multiprocessing
from dotenv import load_dotenv
from colorama import Fore, Style
from requests.exceptions import ReadTimeout

def check_docker_logs():
    command = ["docker", "logs", "--follow", "c3cebaf9f803"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in iter(process.stdout.readline, b''):
        line = line.decode('utf-8').strip()
        print(Fore.GREEN + "Docker Log: " + Style.RESET_ALL + line)  # Print Docker logs in green
        if 'ERR' in line:  # If 'ERR' is in the log line, terminate the script
            print("Error detected in Docker logs:")
            print(line)
            process.terminate()
            os._exit(1)  # Terminate the entire script

if __name__ == '__main__':
    # Start a separate process to check Docker logs
    docker_logs_process = multiprocessing.Process(target=check_docker_logs)
    docker_logs_process.start()

    load_dotenv()

    passphrase = os.getenv('MYSTERIUM_PASSPHRASE')
    proxy_port = "40001"

    base_url = "http://127.0.0.1:4050"

    identities_url = f"{base_url}/identities"
    connection_url = f"{base_url}/connection"
    proposals_url = f"{base_url}/proposals?ip_type=residential"

    try:
        response = requests.get(identities_url, timeout=5)
        data = response.json()
        first_identity_id = data['identities'][0]['id']
    except ReadTimeout:
        pass

    try:
        unlock_url = f"{base_url}/identities/{first_identity_id}/unlock"
        unlock_response = requests.put(unlock_url, json={"passphrase": passphrase}, headers={"Content-Type": "application/json"}, timeout=5)
        if unlock_response.status_code != 202:
            print("Failed to unlock identity.")
            sys.exit()
    except ReadTimeout:
        pass

    try:
        details_url = f"{identities_url}/{first_identity_id}"
        details_response = requests.get(details_url, timeout=5)
        details_data = details_response.json()

        if details_data['registration_status'] != "Registered" or details_data['balance'] <= 0:
            print("Identity is not registered or balance is too low.")
            sys.exit()
    except ReadTimeout:
        pass

    proposals_data = {}

    try:
        proposals_response = requests.get(proposals_url, timeout=5)
        proposals_data = proposals_response.json()
    except ReadTimeout:
        pass

    providers = [(proposal['provider_id'], proposal['location']['country']) 
                 for proposal in proposals_data.get('proposals', []) 
                 if 'location' in proposal]

    choices = [f"{provider_id} ({country})" for provider_id, country in providers]

    questions = [
        inquirer.List('choice',
                      message="Select a VPN location to connect to",
                      choices=choices,
                     ),
    ]

    answers = inquirer.prompt(questions)
    provider_id = answers['choice'].split()[0]
    print(f"You selected: {answers['choice']}")

    # Enhanced Error Handling for Stopping Existing Connections
    for attempt in range(3):  
        try:
            requests.delete(connection_url, verify=False, timeout=5)
            print("Any existing connection has been stopped.")
            break  
        except Exception as e:
            print(f"Error stopping the connection (Attempt {attempt+1}): {e}")
            if attempt == 2: 
                print("Failed to stop existing connection after multiple attempts.")
                sys.exit(1)
            time.sleep(2)  

    # Enhanced Error Handling for Setting Up New Connection
    connection_data = {
        "connect_options": {
            "proxy_port": proxy_port
        },
        "consumer_id": first_identity_id,
        "provider_id": provider_id,
        "service_type": "wireguard"
    }

    for attempt in range(3):
        try:
            put_response = requests.put(connection_url, json=connection_data, headers={"Content-Type": "application/json"}, timeout=5)
            print(f"Connection setup request sent to {answers['choice']}.")
            break
        except Exception as e:
            print(f"Error setting up the connection (Attempt {attempt+1}): {e}")

    print_errors = True

    while True:
        # Check connection status
        try:
            get_response = requests.get(connection_url, timeout=5)
            get_data = get_response.json()
            if get_data['status'] != 'NotConnected':
                print(f"Connection status: {get_data['status']}")
                if get_data['status'] == 'NotConnected':
                    print('Make sure your Mysterium Node Password is correct')
                break
        except ReadTimeout:
            pass
        time.sleep(6)

    # Wait for the Docker log checking process to finish
    docker_logs_process.join()