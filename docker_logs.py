import docker
from dotenv import load_dotenv
import os
import time

load_dotenv()
docker_id = os.getenv('DOCKER_ID')

def check_docker_logs(SHOW_INF, SHOW_DBG, SHOW_DEBUG, SHOW_ERR, LOG_HISTORY):
    client = docker.from_env()
    container = client.containers.get(docker_id)
    since_time = int(time.time()) if not LOG_HISTORY else None
    for line in container.logs(stream=True, since=since_time):
        line = line.decode()
        if ("INF" in line and SHOW_INF) or \
           ("DBG" in line and SHOW_DBG) or \
           (line.startswith("DEBUG:") and SHOW_DEBUG) or \
           ("ERR" in line and SHOW_ERR):
            print(line, end='')
