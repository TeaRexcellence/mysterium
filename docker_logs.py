import os
import subprocess
from colorama import Fore, Style

def check_docker_logs(docker_id):
    command = ["docker", "logs", "--follow", docker_id]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip().decode('utf-8'), flush=True)
    rc = process.poll()
    return rc
