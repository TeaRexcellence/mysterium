import docker
from dotenv import load_dotenv
import os
import time
import re
import sys

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

<<<<<<< Updated upstream
=======
    # Initialize log line with the Docker service name
    log_line = f"🐋 {service_name} ~ "

>>>>>>> Stashed changes
    for line in container.logs(stream=True, since=since_time):
        line = line.decode()

        # Remove timestamp from ERR messages
        if "ERR" in line and SHOW_ERR:
            err_msg = re.sub(r'^.*ERR', 'ERR', line)
<<<<<<< Updated upstream
            print("\n" + err_msg, end='')
            last_log_type = 'ERR'
=======
            print(f"\n🐋 {service_name} ~ " + err_msg, end='', flush=True)  # Added newline at the start
            # Reset counters
            inf_count = 0
            dbg_count = 0
            debug_count = 0
            wrn_count = 0
            # Reset log line
            log_line = f"🐋 {service_name} ~ "
            continue
>>>>>>> Stashed changes
        else:
            # Update counters and print counts
            if CONCATENATE_WARNINGS:
                if "INF" in line and SHOW_INF:
<<<<<<< Updated upstream
                    if last_log_type == 'INF':
                        inf_count += 1
                        sys.stdout.write("\rDocker ~ INF({})".format(inf_count))
                    else:
                        inf_count = 1
                        print("\nDocker ~ INF({})".format(inf_count), end='')
                    last_log_type = 'INF'
                elif "DBG" in line and SHOW_DBG:
                    if last_log_type == 'DBG':
                        dbg_count += 1
                        sys.stdout.write("\rDocker ~ DBG({})".format(dbg_count))
                    else:
                        dbg_count = 1
                        print("\nDocker ~ DBG({})".format(dbg_count), end='')
                    last_log_type = 'DBG'
                elif line.startswith("DEBUG:") and SHOW_DEBUG:
                    if last_log_type == 'DEBUG':
                        debug_count += 1
                        sys.stdout.write("\rDocker ~ DEBUG ({})".format(debug_count))
                    else:
                        debug_count = 1
                        print("\nDocker ~ DEBUG ({})".format(debug_count), end='')
                    last_log_type = 'DEBUG'
                elif "WRN" in line and SHOW_WRN:
                    if last_log_type == 'WRN':
                        wrn_count += 1
                        sys.stdout.write("\rDocker ~ WRN({})".format(wrn_count))
                    else:
                        wrn_count = 1
                        print("\nDocker ~ WRN({})".format(wrn_count), end='')
=======
                    inf_count += 1
                    log_line = log_line.rsplit('INF(', 1)[0] + f"INF({inf_count}),"
                    last_log_type = 'INF'
                elif "DBG" in line and SHOW_DBG:
                    dbg_count += 1
                    log_line = log_line.rsplit('DBG(', 1)[0] + f"DBG({dbg_count}),"
                    last_log_type = 'DBG'
                elif line.startswith("DEBUG:") and SHOW_DEBUG:
                    debug_count += 1
                    log_line = log_line.rsplit('DEBUG(', 1)[0] + f"DEBUG({debug_count}),"
                    last_log_type = 'DEBUG'
                elif "WRN" in line and SHOW_WRN:
                    wrn_count += 1
                    log_line = log_line.rsplit('WRN(', 1)[0] + f"WRN({wrn_count}),"
>>>>>>> Stashed changes
                    last_log_type = 'WRN'
            else:
                if ("INF" in line and SHOW_INF) or \
                   ("DBG" in line and SHOW_DBG) or \
                   (line.startswith("DEBUG:") and SHOW_DEBUG) or \
                   ("WRN" in line and SHOW_WRN):
<<<<<<< Updated upstream
                    print(line)
                    last_log_type = None

    sys.stdout.flush()  # Ensure that the final log line is printed
=======
                    log_line += line + ","
                    last_log_type = None

        # Print the log line
        if last_log_type != 'ERR':
            print("\r" + log_line, end='', flush=True)

    sys.stdout.flush()  # Ensure that the final log line is printed

>>>>>>> Stashed changes
