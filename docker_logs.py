import os
import sys
import docker
import time
import re
from colorama import Fore, Style
from dotenv import load_dotenv
from collections import deque

load_dotenv()  # load environment variables from .env file
docker_id = os.getenv('DOCKER_ID')  # replace 'DOCKER_ID' with your environment variable

def check_docker_logs(SHOW_INF=True, SHOW_DBG=True, SHOW_DEBUG=True, SHOW_ERR=True, SHOW_WRN=True, LOG_HISTORY=False, CONCATENATE_WARNINGS=True):
    while True:
        client = docker.from_env()
        container = client.containers.get(docker_id)  # use the docker_id variable
        service_name = container.name  # Get the Docker service name
        since_time = int(time.time()) if not LOG_HISTORY else None

        # Initialize counters
        inf_count = 0
        dbg_count = 0
        debug_count = 0
        wrn_count = 0

        # Initialize last log type
        last_log_type = None

        # Initialize log line with the Docker service name
        log_line = f"{Fore.LIGHTBLUE_EX}🐋 {service_name} ~ {Style.RESET_ALL}"

        # Initialize a deque as a buffer to store logs temporarily
        log_buffer = deque(maxlen=10)

        for line in container.logs(stream=True, since=since_time):
            line = line.decode()

            # Remove extra spaces
            line = re.sub(' +', ' ', line)

            # Add the line to the buffer
            log_buffer.append(line)

            # Process the lines in the buffer
            while log_buffer:
                line = log_buffer.popleft()

                # Remove timestamp from ERR messages
                if "ERR" in line and SHOW_ERR:
                    err_msg = re.sub(r'^.*ERR', 'ERR', line)
                    print(f"\n{Fore.LIGHTBLUE_EX}🐋 {service_name} ~ {Fore.RED}" + err_msg + Style.RESET_ALL, end='', flush=True)
                    # Reset counters
                    inf_count = 0
                    dbg_count = 0
                    debug_count = 0
                    wrn_count = 0
                    # Reset log line
                    log_line = f"{Fore.LIGHTBLUE_EX}🐋 {service_name} ~ {Style.RESET_ALL}"
                    time.sleep(8)  # wait for 8 seconds before restarting the function
                    break  # Break the inner loop and process the remaining logs in the buffer
                else:
                    # Update counters and print counts
                    if CONCATENATE_WARNINGS:
                        if "INF" in line and SHOW_INF:
                            inf_count += 1
                            if last_log_type != 'INF':
                                dbg_count = 0
                                debug_count = 0
                                wrn_count = 0
                                log_line += f"{Fore.GREEN}INF({inf_count}),{Style.RESET_ALL}"
                            else:
                                log_line = log_line.rsplit('INF(', 1)[0] + f"{Fore.GREEN}INF({inf_count}),{Style.RESET_ALL}"
                            last_log_type = 'INF'
                        elif "DBG" in line and SHOW_DBG:
                            dbg_count += 1
                            if last_log_type != 'DBG':
                                inf_count = 0
                                debug_count = 0
                                wrn_count = 0
                                log_line += f"{Fore.GREEN}DBG({dbg_count}),{Style.RESET_ALL}"
                            else:
                                log_line = log_line.rsplit('DBG(', 1)[0] + f"{Fore.GREEN}DBG({dbg_count}),{Style.RESET_ALL}"
                            last_log_type = 'DBG'
                        elif line.startswith("DEBUG:") and SHOW_DEBUG:
                            debug_count += 1
                            if last_log_type != 'DEBUG':
                                inf_count = 0
                                dbg_count = 0
                                wrn_count = 0
                                log_line += f"{Fore.GREEN}DEBUG({debug_count}),{Style.RESET_ALL}"
                            else:
                                log_line = log_line.rsplit('DEBUG(', 1)[0] + f"{Fore.GREEN}DEBUG({debug_count}),{Style.RESET_ALL}"
                            last_log_type = 'DEBUG'
                        elif "WRN" in line and SHOW_WRN:
                            wrn_count += 1
                            if last_log_type != 'WRN':
                                inf_count = 0
                                dbg_count = 0
                                debug_count = 0
                                log_line += f"{Fore.YELLOW}WRN({wrn_count}),{Style.RESET_ALL}"
                            else:
                                log_line = log_line.rsplit('WRN(', 1)[0] + f"{Fore.YELLOW}WRN({wrn_count}),{Style.RESET_ALL}"
                            last_log_type = 'WRN'
                    else:
                        if ("INF" in line and SHOW_INF) or \
                        ("DBG" in line and SHOW_DBG) or \
                        (line.startswith("DEBUG:") and SHOW_DEBUG) or \
                        ("WRN" in line and SHOW_WRN):
                            log_line += line + ","
                            last_log_type = None

                # Print the log line
                if last_log_type != 'ERR':
                    print("\r" + log_line, end='', flush=True)

            else:
                # If the inner loop completed without break (no ERR found), continue to the next line
                continue  # Continue to the next line

            break  # An ERR was found, restart the function

        sys.stdout.flush()  # Ensure that the final log line is printed
