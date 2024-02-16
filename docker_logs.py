import os
import subprocess

def check_docker_logs(docker_id):
    command = ["docker", "logs", "--follow", docker_id]
    process = subprocess.run(command, capture_output=True, text=True)
    print(process.stdout)
