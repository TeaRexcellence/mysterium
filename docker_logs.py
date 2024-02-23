import docker
from dotenv import load_dotenv
import os
import time
import re
import sys
#lol
load_dotenv()
docker_id = os.getenv('DOCKER_ID')

def check_docker_logs(SHOW_INF, SHOW_DBG, SHOW_DEBUG, SHOW_ERR, SHOW_WRN, LOG_HISTORY, CONCATENATE_WARNINGS):
    client = docker.from_env()
    container = client.containers.get(docker_id)
    service_name = container.name  # Get the Docker service name
    since_time = int(time.time()) if not LOG_HISTORY else None

    # Initialize counters
    inf_count = 0
    dbg_count = 0
    debug_count = 0
    wrn_count = 0

    # Initialize last log type
    last_log_type = None

    # Initialize set for duplicate prevention
    seen_lines = set()

    # Initialize log line with the Docker service name
    log_line = f"🐋 {service_name} ~ "

    for line in container.logs(stream=True, since=since_time):
        line = line.decode()

        # Remove extra spaces
        line = re.sub(' +', ' ', line)

        # Check for duplicates before processing
        if line in seen_lines:
            continue
        seen_lines.add(line)

        # Remove timestamp from ERR messages
        if "ERR" in line and SHOW_ERR:
            err_msg = re.sub(r'^.*ERR', 'ERR', line)
            print(f"\n🐋 {service_name} ~ " + err_msg, end='', flush=True)
            # Reset counters
            inf_count = 0
            dbg_count = 0
            debug_count = 0
            wrn_count = 0
            # Reset log line
            log_line = f"🐋 {service_name} ~ "
            continue
        else:
            # Update counters and print counts
            if CONCATENATE_WARNINGS:
                if "INF" in line and SHOW_INF:
                    inf_count += 1
                    if last_log_type != 'INF':
                        dbg_count = 0
                        debug_count = 0
                        wrn_count = 0
                        log_line += f"INF({inf_count}),"
                    else:
                        log_line = log_line.rsplit('INF(', 1)[0] + f"INF({inf_count}),"
                    last_log_type = 'INF'
                elif "DBG" in line and SHOW_DBG:
                    dbg_count += 1
                    if last_log_type != 'DBG':
                        inf_count = 0
                        debug_count = 0
                        wrn_count = 0
                        log_line += f"DBG({dbg_count}),"
                    else:
                        log_line = log_line.rsplit('DBG(', 1)[0] + f"DBG({dbg_count}),"
                    last_log_type = 'DBG'
                elif line.startswith("DEBUG:") and SHOW_DEBUG:
                    debug_count += 1
                    if last_log_type != 'DEBUG':
                        inf_count = 0
                        dbg_count = 0
                        wrn_count = 0
                        log_line += f"DEBUG({debug_count}),"
                    else:
                        log_line = log_line.rsplit('DEBUG(', 1)[0] + f"DEBUG({debug_count}),"
                    last_log_type = 'DEBUG'
                elif "WRN" in line and SHOW_WRN:
                    wrn_count += 1
                    if last_log_type != 'WRN':
                        inf_count = 0
                        dbg_count = 0
                        debug_count = 0
                        log_line += f"WRN({wrn_count}),"
                    else:
                        log_line = log_line.rsplit('WRN(', 1)[0] + f"WRN({wrn_count}),"
                    last_log_type = 'WRN'

        # Print the log line
        print("\r" + log_line, end='', flush=True)

    sys.stdout.flush()  # Ensure that the final log line is printed
