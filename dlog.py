import subprocess

def check_docker_logs(docker_id):
    command = ["docker", "logs", "--follow", docker_id]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in iter(process.stdout.readline, b''):
        print(line.decode(), end='')

if __name__ == '__main__':
    docker_id = "3f09855aaae6"  # replace with your Docker container ID
    check_docker_logs(docker_id)
