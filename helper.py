import socket, os
from Crypto.Cipher import DES3
from os import system, name 

def clearScreen(): 
    _ = system('clear')

def printWelcomeMessage():
    print("\n\033[1mWelcome !!\033[0m")
    print("New User?   \x1B[33mSign up <Name> <Roll no.> <Password>\033[0m")
    print("Already have an account?   \x1B[33mLogin <Name||Roll no.> <Password>\n\033[0m")

def printAllCommands():
    print("\n\033[1mAvailable Commands\033[0m")                                   
    print("\x1B[33mSend <Name||Roll no.> <message>")                        # 4 ways
    print("Send_file file_name <Name||Roll no.>")   
    print("Send_group <No. of groups> <Group no.(s)> <message>")    # 4 ways    send_group 2 g1 g2 this is my g2 dsjfkdlsajfkl
    print("Send_group_File <File_Name>  <No. of groups> <Group no.(s)>")
    print("List")
    print("Create <Group name>")
    print("Join <Group name>")
    print("Show_my_groups\n\x1B[0m")

def connectToLoadBalancer(LoadBalancerIp, LoadBalancerport):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((LoadBalancerIp, LoadBalancerport))
    return s

def sendRecvMessage(message, socket):
    socket.sendall(message.encode('utf-8'))                          #SIGN@UP@U1R1@P1@IP@PORT
    data = socket.recv(1024).decode("utf-8")
    return data 

def encrypt_msg(key,msg):                               
    final_key= (bytearray(str(key), 'utf-16'))[-24:]
    msg="GAR"+msg                                           #Adding 3 GARBAGE characters
    cipher = DES3.new(final_key, DES3.MODE_CFB)
    return cipher.encrypt(msg.encode('utf-16'))

def decrypt_msg(key,msg):
    final_key= (bytearray(str(key), 'utf-16'))[-24:]
    cipher = DES3.new(final_key, DES3.MODE_CFB)
    return cipher.decrypt(msg)                           #Remove first 4 characters while decoding it.
    
def encrypt_file(key,msg):
    final_key= (bytearray(str(key), 'utf-16'))[-24:]
    cipher = DES3.new(final_key, DES3.MODE_CFB)
    return cipher.encrypt(msg)


