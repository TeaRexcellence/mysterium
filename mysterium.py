import requests
import random
import sys
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

passphrase = os.getenv('MYSTERIUM_PASSPHRASE')  # Get the passphrase from .env file
proxy_port = "40001"

# Base URL for API requests
base_url = "http://127.0.0.1:4050"

# Endpoints
identities_url = f"{base_url}/identities"
connection_url = f"{base_url}/connection"
proposals_url = f"{base_url}/proposals?ip_type=residential"

# Get the first identity ID
response = requests.get(identities_url)
data = response.json()
first_identity_id = data['identities'][0]['id']

# Unlock the identity before Step 2
unlock_url = f"{base_url}/identities/{first_identity_id}/unlock"
unlock_response = requests.put(unlock_url, json={"passphrase": passphrase}, headers={"Content-Type": "application/json"})
if unlock_response.status_code != 202:
    print("Failed to unlock identity.")
    sys.exit()

# Check the details of that identity
details_url = f"{identities_url}/{first_identity_id}"
details_response = requests.get(details_url)
details_data = details_response.json()

# Exit if the identity is not registered or the balance is too low
if details_data['registration_status'] != "Registered" or details_data['balance'] <= 0:
    print("Identity is not registered or balance is too low.")
    sys.exit()

# Fetch provider IDs from proposals
proposals_response = requests.get(proposals_url)
proposals_data = proposals_response.json()
providers = [proposal['provider_id'] for proposal in proposals_data['proposals']]
provider_id = random.choice(providers)  # Select a random provider ID

# Stop any current connections right before setting up a new connection
try:
    requests.delete(connection_url, verify=False)  # Assuming ignoring SSL certificate verification
    print("Any existing connection has been stopped.")
except Exception as e:
    print(f"Error stopping the connection: {e}")
    sys.exit()

#  Set up a new connection using the PUT request
connection_data = {
    "connect_options": {
        "proxy_port": proxy_port
    },
    "consumer_id": first_identity_id,
    "provider_id": provider_id,
    "service_type": "wireguard"
}

try:
    put_response = requests.put(connection_url, json=connection_data, headers={"Content-Type": "application/json"})
    print("Connection setup request sent.")
except Exception as e:
    print(f"Error setting up the connection: {e}")

# Check the status of the new connection
try:
    get_response = requests.get(connection_url)
    get_data = get_response.json()
    print(f"Connection status: {get_data['status']}")
except Exception as e:
    print(f"Error getting the connection status: {e}")
