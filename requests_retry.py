import requests
import sys
import time
from requests.exceptions import ReadTimeout

def retry_request(url, method, json=None, headers=None, max_retries=5):
    for attempt in range(max_retries):
        try:
            if method == 'get':
                response = requests.get(url, timeout=5)
            elif method == 'put':
                response = requests.put(url, json=json, headers=headers, timeout=5)
            elif method == 'delete':
                response = requests.delete(url, verify=False, timeout=5)
            return response
        except ReadTimeout:
            print(f"Connection failed. Retrying attempt {attempt+1}...")
            if attempt == max_retries - 1:
                print("Max retries reached. Exiting.")
                sys.exit(1)
            time.sleep(2)
