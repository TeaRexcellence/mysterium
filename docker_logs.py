import subprocess
from dotenv import load_dotenv
import os

load_dotenv()
docker_id = os.getenv('DOCKER_ID')

def check_docker_logs():
    command = ["docker", "logs", "--follow", docker_id]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        print(line.decode(), end='')
