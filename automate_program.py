import subprocess, os, sys
from subprocess import Popen, PIPE, call

server_path = "./server.py"
client_path = "./clent.py"

number_of_servers = None
number_of_clients = None

if len(sys.argv) < 2:
    number_of_servers = 3
else:
    number_of_servers = int(sys.argv[1])


for i in range(number_of_servers):
    status = subprocess.call("gnome-terminal -- python3 " + server_path, shell = True)


# for i in range(number_of_clients):
#      status = subprocess.call("gnome-terminal -- python3 " + client_path, shell=True)
