import threading, socket, os
import sys, hashlib
from random import randrange
import base64
from Crypto.Cipher import DES3
from os import system, name 
from time import sleep
from helper import *

delimiter = "@"
path_to_store_files = './'
prime = "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF"

class User(object):
    def __init__(self, load_port):
        self.load_bal_Addr= "127.0.0.1"
        self.load_bal_port= int(load_port)
        self.username = ""
        self.isLoggedIn = False
        self.groupkeys = dict()   # grp name -> keys map
        self.q = int(prime, 16)
        self.alpha = 2

    def set_username(self,usern):
        self.username = usern

    def join_group(self,groupname,key):
        self.groupkeys[groupname] = key

    def set_groupKeys(self, grps_info):
        if len(grps_info) > 2:
            for i in range(1,len(grps_info),2):
                self.groupkeys[grps_info[i]] = grps_info[i+1]

    def show_my_groups(self):
        if not self.groupkeys:
            print("Not a member of any groups")
            return
        for groupname in self.groupkeys.keys():
            print(groupname)

    def handle_request(self,connection):                     ## DHK recv side
        data = connection.recv(1024).decode('utf-8')         ##  Assume this to be public key of Sender  2$username$public_key(peer)
        if data.split(delimiter)[0] == '2':
            try:
                sender_username = data.split(delimiter)[1]
                data = data.split(delimiter)[2]                     #Public key client
                user = str(randrange(1000)) + str(self.username)
                private_key = hashlib.sha256(user.encode())     
                public_key = pow(self.alpha, int(private_key.hexdigest(),16), self.q)

                connection.send(str(public_key).encode('utf-8'))        #Sending my public key
                shared_key = pow(int(data),int(private_key.hexdigest(),16),self.q) 
               
                data=connection.recv(1024)
                decyrpted_msg = decrypt_msg(shared_key,data)
                print(sender_username," : ",decyrpted_msg.decode('utf-16')[4:])
            except Exception:
                print("Message not Received, try again")
        
        elif data.split(delimiter)[0] == '5':
            try:
                sender_username = data.split(delimiter)[1]
                data = data.split(delimiter)[2]
                user = str(randrange(1000)) + str(self.username)
                private_key = hashlib.sha256(user.encode())     
                public_key = pow(self.alpha, int(private_key.hexdigest(),16), self.q)

                connection.send(str(public_key).encode('utf-8'))        
                shared_key = pow(int(data),int(private_key.hexdigest(),16),self.q)  
                
                filename=connection.recv(1024).decode('utf-8')
                filename="Received_"+filename
                print("Received from ",sender_username," : ",filename)
                c=1
                f=open(filename, 'ab+')
                bytes_read = connection.recv(40960000)
                print(len(bytes_read)," ",c)
                while bytes_read:
                    decyrpted_msg = decrypt_msg(shared_key,bytes_read)
                    f.write(decyrpted_msg)
                    c+=1
                    bytes_read = connection.recv(40960000)
                    print(len(bytes_read)," ",c)
                
                f.close()
            except Exception:
                print("Message not sent, try again")

        elif data.split(delimiter)[0] == '3':               # received from server (grp)    3$group_name$msg_from_group
            sender_grp_name = data.split(delimiter)[1]
            print(sender_grp_name," : ",data.split(delimiter)[2][3:])
            #data = connection.recv(1024)
        
        #Group files
        elif data.split(delimiter)[0] == '4':   # received file from server (grp)    4$file_name$group_name
            # print("data4 ",data)
            try:
                filename = data.split(delimiter)[1]
                group = data.split(delimiter)[2]
                filepath = path_to_store_files + "Received_" + filename
                bytes_to_read = 4096
                with open(filepath, 'wb') as f:
                    file_data = connection.recv(bytes_to_read)
                    while file_data:
                        f.write(file_data)
                        file_data = connection.recv(bytes_to_read)
                print("File downloaded sent from group",group)
            except Exception as e:
                print(e)


        connection.close()
        return

    def client_as_server(self,host_addr, port):             ##      Receiver of msg
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host_addr, int(port)))
        # print(s.getsockname()[1])

        thread_list=[]
        while True:
            s.listen()
            conn, addr = s.accept()
            thread = threading.Thread(target = self.handle_request, args= (conn, ))
            thread_list.append(thread)
            thread.start()

    def client_connection_with_other_client(self,ip,port, msg,typeofmsg):           ## Sender of msg
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip,int(port)))
        except Exception:
            print("Client is not Available")
            return
        
        user = str(randrange(1000)) + str(self.username)                  #   Implement DHK sender side here!
        private_key = hashlib.sha256(user.encode())                       # 32 Bytes no.
        public_key_client= pow(self.alpha, int(private_key.hexdigest(),16), self.q)
        
        if typeofmsg == 'm':
            public_key_client = '2'+delimiter+ self.username + delimiter+ str(public_key_client)
            s.send(public_key_client.encode('utf-8'))                          #Sending my public key
            public_key_recvr = s.recv(1024).decode("utf-8")
            shared_key = pow(int(public_key_recvr),int(private_key.hexdigest(),16),self.q)
            encyrpted_msg = encrypt_msg(shared_key,msg)
            s.send(encyrpted_msg)

        elif typeofmsg == 'f':
            public_key_client = '5'+delimiter+ self.username + delimiter + str(public_key_client)
            s.send(public_key_client.encode('utf-8')) 
            public_key_recvr = s.recv(1024).decode("utf-8")
            shared_key = pow(int(public_key_recvr),int(private_key.hexdigest(),16),self.q)
            print("filename: ",msg)
            s.send(msg.encode('utf-8'))
            
            f=open("./"+msg,'rb')                 
            line = f.read()
            while line:
                encyrpted_msg = encrypt_file(shared_key,line)
                s.sendall(encyrpted_msg)
                line = f.read()
            
            f.close()
            
        s.close()

    def interact_with_server(self):
        printAllCommands()
        
        while True:
            command = input(":")
            tokens = command.split(' ')
            command_type = tokens[0].lower()
            if (command_type == "send"):     
                if len(tokens) <  3:
                    print("Invalid args to <send>")
                    continue
                
                s = connectToLoadBalancer(self.load_bal_Addr,self.load_bal_port)
                padded_msg = "SEND"+delimiter+"dummy"+delimiter+self.username+delimiter+tokens[1]       
                data = sendRecvMessage(padded_msg, s)     #  1@IP@PORT of receiver.
                # print("receiver details received",data)
                s.close()
                
                isSuccess = data.split(delimiter)[0]
                if (isSuccess =='1'):
                    recv_ip = data.split(delimiter)[1]
                    recv_port = data.split(delimiter)[2]
                    msg=""
                    for i in range(2,len(tokens)):
                        msg=msg+tokens[i]+" "
                    typeofmsg='m'
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (recv_ip,recv_port,msg,typeofmsg)) 
                    thread.start()
                else:
                    error_message = data.split(delimiter)[1]
                    print(error_message)
            
            elif (command_type == "send_file"):      #send_file file_name peername -FORMAT by pdf
                if len(tokens) <  3:
                    print("Invalid args to <send>")
                    continue
                s = connectToLoadBalancer(self.load_bal_Addr,self.load_bal_port)      #send dummy username peername FORMAT BY SERVER
                padded_msg = "SEND"+delimiter+"DUMMY"+delimiter+self.username+delimiter+tokens[2]
                data = sendRecvMessage(padded_msg, s)     #  1@IP@PORT of receiver.
                s.close()
                
                isSuccess = data.split(delimiter)[0]
                if (isSuccess =='1'):
                    recv_ip = data.split(delimiter)[1]
                    recv_port = data.split(delimiter)[2]
                    typeofmsg = 'f'
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (recv_ip,recv_port,tokens[1],typeofmsg)) 
                    thread.start()
                else:
                    error_message = data.split(delimiter)[1]
                    print(error_message)
            
            ##SEND-GROUP 
            elif (command_type == "send_group"):              #send_group no_of_grps grpname(s) msg 
                if len(tokens) < 4:
                    print("Invalid args to <send_group>")
                    continue
                try:
                    no_of_grps = int(tokens[1])
                except:
                    print("No. of groups must be an integer")
                    continue
                groups = []
                for i in range(no_of_grps):
                    if tokens[i+2] in self.groupkeys.keys():
                        groups.append(tokens[i+2])
                    else:
                        print("You are not a part of ",tokens[i+2],"group")
                try:
                    msg = "GAR"
                    for i in range(no_of_grps + 2,len(tokens)):
                        msg=msg+tokens[i]+" "
                except Exception:
                    print("No message provided")
                    continue
                if not groups:
                    print("Message not sent! Not a member of any of the groups")
                    continue

                s = connectToLoadBalancer(self.load_bal_Addr,self.load_bal_port)
                grp_str = delimiter.join(groups)
                padded_msg = "SEND_GROUP"+delimiter+"DUMMY"+delimiter+self.username+delimiter+msg+delimiter+grp_str    # send_group@DUMMY@USERNAME@MESSAGE@G1@G2...        
                data = sendRecvMessage(padded_msg, s)
                isSuccess = data.split(delimiter)[0]
                if (isSuccess == '1'):
                    print("Message Sent!")
                else:
                    error_message = data.split(delimiter)[1]
                    print(error_message)
                s.close()

            ##SEND GROUP FILE
            elif (command_type == "send_group_file"):     #CLIENT- send_group_file abc.txt 2 g1 g2
                if len(tokens) < 4:
                    print("Invalid args to <send_group>")
                    continue
                #no_of_grps=None
                try:
                    no_of_grps = int(tokens[2])
                except:
                    print("No. of groups must be an integer")
                groups = []
                for i in range(no_of_grps):
                    if tokens[i+3] in self.groupkeys.keys():
                        groups.append(tokens[i+3])
                    else:
                        print("You are not a part of ",tokens[i+3],"group")
                if not groups:
                    print("Message not sent! Not a member of any of the groups")
                    continue
                
                s = connectToLoadBalancer(self.load_bal_Addr,self.load_bal_port)
                grp_str = delimiter.join(groups)
                print("grp_str is ", grp_str)
                padded_msg = "SEND_GROUP_FILE"+ delimiter+ tokens[1] + delimiter + self.username + delimiter + grp_str  # send_group@DUMMY@USERNAME@MESSAGE@G1@G2...        
                s.sendall(padded_msg.encode('utf-8'))
                print(padded_msg)                
                
                #Make the client wait for some time befor sending file
                sleep(.5)

                filepath = './'
                with open(filepath + tokens[1],'rb') as f:
                    bytes_to_read = 1024
                    file_data=f.read(bytes_to_read)
                    while file_data:
                        s.sendall(file_data)
                        file_data = f.read(bytes_to_read)

                print("File has been sent")
                s.close()

            elif (command_type == "list"):                            #LIST  FORMAT PDF
                if len(tokens) != 1:
                    print("Invalid args to <list>")
                    continue
                
                s = connectToLoadBalancer(self.load_bal_Addr,self.load_bal_port)
                padded_msg = "LIST"+delimiter+"groups"+delimiter+self.username      #LIST@groups@user1- FORMAT SERVER        
                data = sendRecvMessage(padded_msg, s)                         # 1@grpname@num_users@grpname@num
                isSuccess = data.split(delimiter)[0]
                if (isSuccess == '1'):                                                                          
                    grps_list=data[2:].split(delimiter)
                    print(grps_list, "len = ", len(grps_list))
                    if len(grps_list) < 2:
                        print("No groups found!")
                    else:
                        for i in range(0,len(grps_list),2):
                            print(grps_list[i]," : ",grps_list[i+1])                                  
                else:
                    error_message = data.split(delimiter)[1]
                    print(error_message)
                s.close()

            elif (command_type == "join"):                           #JOIN g1-FORMAT PDF
                if len(tokens) != 2:
                    print("Invalid args to <join>")
                    continue
                if tokens[1] in self.groupkeys.keys():
                    print("You are already a member of the group")
                    continue
                s = connectToLoadBalancer(self.load_bal_Addr,self.load_bal_port)
                padded_msg="JOIN"+delimiter+tokens[1]+delimiter+self.username                   
                data = sendRecvMessage(padded_msg, s)                         # 1@grpname@num_users@grpname@num
                isSuccess = data.split(delimiter)[0]          #JOIN@group1@user2 -FORMAT SERVER        # 1@grp_key
                if (isSuccess == '1'):
                    print("Group Joined! ")
                    # print(data.split(delimiter)[1])        # server returns key of that group
                    self.groupkeys[tokens[1]] = data.split(delimiter)[1]
                else:
                    error_message = data.split(delimiter)[1]
                    print(error_message)
                
                s.close()
            
            elif (command_type == "create"):             #create g1 FORMAT PDF
                if len(tokens) != 2:
                    print("Invalid args to <create>")
                    continue
                if tokens[1] in self.groupkeys.keys():
                    print("You are already a member of the group")
                    continue      
                s = connectToLoadBalancer(self.load_bal_Addr,self.load_bal_port)
                padded_msg="CREATE"+delimiter+tokens[1]+delimiter+self.username        
                data = sendRecvMessage(padded_msg, s)                 #CREATE@group1@user1 -FORMAT SERVER 
                isSuccess = data.split(delimiter)[0]
                if (isSuccess == '1'):               #1@group_created@randomkey
                    print("Group Created! ")
                    self.groupkeys[tokens[1]] = data.split(delimiter)[2]
                else:
                    error_message = data.split(delimiter)[1]
                    print(error_message)
                s.close()
            elif (tokens[0].upper() == "SHOW_MY_GROUPS"):
                self.show_my_groups()

def main():
    if len(sys.argv) != 3:
        print("Type in the format : client.py <client_PORT> <load_balancer_port>")
        return
    #---Listening for other clients or servers
    client_IP = "127.0.0.1"
    client_PORT = sys.argv[1]
    print("Listening on ",client_IP,client_PORT)

    thisUser = User(sys.argv[2])
    
    client_as_server_thread = threading.Thread(target = thisUser.client_as_server, args=(client_IP, client_PORT))
    client_as_server_thread.start()

    clearScreen()
    printWelcomeMessage()
    
    while True:
        command = input(":")
        tokens = command.split(' ')
        if tokens[0] == '' or len(tokens) < 3:
            print("Invalid Command")
            continue
        
        signup_check=tokens[0].lower()+" "+tokens[1].lower()
        command_type = tokens[0].lower()
        if (command_type == "sign"):                        #SIGN UP U1 R1 P1  #Indx-0 1 2 3 4 #LEN-5
            if len(tokens) != 5:
                print("Invalid args to <Signup>")
                continue
            
            #---Connecting to Load Balancer    
            s = connectToLoadBalancer(thisUser.load_bal_Addr, thisUser.load_bal_port)                    
            username = tokens[2] + tokens[3]                                             
            padded_msg = "SIGN"+delimiter+"UP"+delimiter+username+delimiter+tokens[4]+delimiter+client_IP+delimiter+client_PORT #SIGN@UP@U1R1@P1@IP@PORT
            data = sendRecvMessage(padded_msg, s)
            isSuccess = data.split(delimiter)[0]
            if (isSuccess == '1'):
                print("Successfully SIGNED UP!")
            else:
                error_message = data.split(delimiter)[1]
                print(error_message)
            s.close()
        
        elif (command_type == "login"):                              #login username passwd
            if len(tokens) != 3:
                print("Invalid args to <Login>")
                continue            
            
            s = connectToLoadBalancer(thisUser.load_bal_Addr, thisUser.load_bal_port)
            padded_msg = "SIGN"+delimiter+"IN"+delimiter+tokens[1]+delimiter+tokens[2]+delimiter+client_IP+delimiter+client_PORT   #SIGN@IN@U1@P1
            data = sendRecvMessage(padded_msg, s)
            isSuccess = data.split(delimiter)[0]
            if (isSuccess =='1'):
                clearScreen()
                print("Successfully LOGGED IN!")
                thisUser.set_username(tokens[1])
                grps_info = data.split(delimiter)
                thisUser.set_groupKeys(grps_info)
                thisUser.interact_with_server()
                break
            else:
                error_message = data.split(delimiter)[1]
                print(error_message)
            s.close()
        else:
            print("Please signup/login first!")


if __name__ == '__main__':
    main()

# 440 - 451
# list of groups empty check
# error handling signup login