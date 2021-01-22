path =  "python3 ~/server_side.py"
path2 = "~/server_side.py"
# print(path)

path3= "'/home/jarves/NewFolder/IIITH Classes/Second Semester/System and Network Security/Assignment1/End-to-end-messaging-system/server_side.py'"


import subprocess, os
from subprocess import Popen, PIPE, call

for i in range(3):
    
    status = subprocess.call("gnome-terminal -- python3 " + path3, shell=True)
