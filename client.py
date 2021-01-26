import threading, socket, os
import sys, hashlib
from random import randrange
import base64
from Crypto.Cipher import DES3

delimiter = "@"
path_to_store_files = '../Client_path' 

class User(object):
    def __init__(self, load_port):
        self.load_bal_Addr= "127.0.0.1"
        self.load_bal_port= int(load_port)
        self.username = ""
        self.isLoggedIn = False
        self.groupkeys = dict()   # grp name -> keys map
        self.q = int("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF", 16)
        self.alpha = 2
        # 2410312426921032588552076022197566074856950548502459942654116941958108831682612228890093858261341614673227141477904012196503648957050582631942730706805009223062734745341073406696246014589361659774041027169249453200378729434170325843778659198143763193776859869524088940195577346119843545301547043747207749969763750084308926339295559968882457872412993810129130294592999947926365264059284647209730384947211681434464714438488520940127459844288859336526896320919633919

    def set_username(self,usern):
        self.username = usern

    def join_group(self,groupname,key):
        self.groupkeys[groupname] = key
    def show_my_groups(self):
        for groupname in self.groupkeys.keys():
            print(groupname,":",self.groupkeys[groupname])


    def encrypt_msg(self,key,msg):                                  
        final_key= (bytearray(str(key), 'utf-16'))[-24:]
        msg="GAR"+msg                                           #Adding 3 GARBAGE characters
        cipher = DES3.new(final_key, DES3.MODE_CFB)
        return cipher.encrypt(msg.encode('utf-16'))
    
    def decrypt_msg(self,key,msg):
        final_key= (bytearray(str(key), 'utf-16'))[-24:]
        cipher = DES3.new(final_key, DES3.MODE_CFB)
        return cipher.decrypt(msg)                           #Remove first 4 characters while decoding it.



    def handle_request(self,connection):                     ## DHK recv side
        data = connection.recv(1024).decode('utf-8')         ##  Assume this to be public key of Sender  2$public_key(peer)
        if data.split(delimiter)[0] == '2':
            data = data.split(delimiter)[1]                 #Public key client
            user = str(randrange(1000)) + str(self.username)
            private_key = hashlib.sha256(user.encode())     # 32 Bytes no.
            public_key = pow(self.alpha, int(private_key.hexdigest(),16), self.q)

            connection.send(str(public_key).encode('utf-8'))        #Sending my public key
            shared_key = pow(int(data),int(private_key.hexdigest(),16),self.q) 
           
            data=connection.recv(1024)
            decyrpted_msg=self.decrypt_msg(shared_key,data)
            print("Msg: ",decyrpted_msg.decode('utf-16')[4:])

        elif data.split(delimiter)[0] == '3':       # received from server (grp)    3$group_name$msg_from_group
            sender_grp_name = data.split(delimiter)[1]
            #cipher = DES3.new(self.groupkeys[sender_grp_name], DES3.MODE_CFB)
            #decyrpted_msg = cipher.decrypt(data.split(delimiter)[2])
            print("Msg: ",data.split(delimiter)[2])
            #data = connection.recv(1024)
        
        #Group files
        elif data.split(delimiter[0] == '4'):   # received file from server (grp)    4$file_name$group_name
            filename = data.split(delimiter)[1]
            group = data.split(delimiter)[2]
            filepath = path_to_store_files + filename
            bytes_to_read = 1024
            with open(filepath, 'wb') as f:
                file_data = f.recv(bytes_to_read)
                while file_data:
                    f.write(file_data)
                    file_data = f.recv(bytes_to_read)
            print("File downloaded sent from group",group)

        print("Connection is closed")
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

    def client_connection_with_other_client(self,ip,port, msg):           ## Sender of msg
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("ip, port = ",ip,port)
        s.connect((ip,int(port)))
        user = str(randrange(1000)) + str(self.username)                  #   Implement DHK sender side here!
        private_key = hashlib.sha256(user.encode())                       # 32 Bytes no.
        public_key_client= pow(self.alpha, int(private_key.hexdigest(),16), self.q)
        public_key_client = '2'+delimiter+str(public_key_client)
        s.send(public_key_client.encode('utf-8'))                          #Sending my public key

        public_key_recvr = s.recv(1024).decode("utf-8")

        shared_key = pow(int(public_key_recvr),int(private_key.hexdigest(),16),self.q)

        encyrpted_msg=self.encrypt_msg(shared_key,msg)
        s.send(encyrpted_msg)
        s.close()

    def interact_with_server(self):
        print("\nAvailable Commands")
        print("Send <Name||Roll no.> <message>")    # 4 ways
        print("Send_group <No. of groups> <Group no.(s)> <message>")    # 4 ways    send_group 2 g1 g2 this is my g2 dsjfkdlsajfkl
        print("Send_group_File <File_Name>  <No. of groups> <Group no.(s)>")
        print("List")
        print("Create <Group name>")
        print("Join <Group name>\n")
        while True:
            org_msg=input(":")
            # padded_msg=appending_dollar(org_msg)+client_IP+"@"+client_PORT
            tokens=org_msg.split(' ')
            if (tokens[0].lower()=="send"):     
                if len(tokens) <  3:
                    print("Invalid args to <send>")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr,self.load_bal_port))
                #send usnername msg -FORMAT by pdf
                #SEND@dummy@username_of_sender@username_of_recv -FORMAT by SERVER
                padded_msg = "SEND"+delimiter+"dummy"+delimiter+self.username+delimiter+tokens[1]       
                s.send(padded_msg.encode('utf-8'))
                data = s.recv(1024).decode("utf-8")     #  1@IP@PORT of receiver.
                print("receiver details received",data)
                s.close()
                if (data.split(delimiter)[0]=='1'):
                    recv_ip=data.split(delimiter)[1]
                    recv_port=data.split(delimiter)[2]
                    msg=""
                    for i in range(2,len(tokens)):
                        msg=msg+tokens[i]+" "
                    #msg="GAR"+msg
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (recv_ip,recv_port,msg)) 
                    thread.start()
                else:
                    print(data.split(delimiter)[1])

            ##SEND-GROUP 
            elif (tokens[0].lower()=="send_group"):              #send_group no_of_grps grpname(s) msg 
                if len(tokens) < 4:
                    print("Invalid args to <send_group>")
                    continue
                try:
                    no_of_grps = int(tokens[1])
                except:
                    print("No. of groups must be an integer")
                groups = []
                for i in range(no_of_grps):
                    if tokens[i+2] in self.groupkeys.keys():
                        groups.append(tokens[i+2])
                    else:
                        print("You are not a part of ",tokens[i+2],"group")
                msg = "GAR"+tokens[no_of_grps+2]
                if not groups:
                    print("Message not sent! Not a member of any of the groups")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr,self.load_bal_port))
                grp_str = delimiter.join(groups)
                padded_msg = "SEND_GROUP"+delimiter+"DUMMY"+delimiter+self.username+delimiter+msg+delimiter+grp_str    # send_group@DUMMY@USERNAME@MESSAGE@G1@G2...        
                s.send(padded_msg.encode('utf-8'))
                data = s.recv(1024).decode("utf-8") 
                if (data.split(delimiter)[0]=='1'):
                    print("Message Sent!")
                else:
                    print(data.split(delimiter)[1])
                s.close()

            ##SEND-GROUP FILE
            elif (tokens[0].lower()=="send_group_file"):     #CLIENT- send_group_file abc.txt 2 g1 g2
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
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr,self.load_bal_port))
                grp_str = delimiter.join(groups)

                print("grp_str is ", grp_str)
                padded_msg = "SEND_GROUP_FILE"+ delimiter+ tokens[1] + delimiter+ self.username+ delimiter+ grp_str    # send_group@DUMMY@USERNAME@MESSAGE@G1@G2...        
                s.sendall(padded_msg.encode('utf-8'))
                print(padded_msg)                
                filepath = './'
                with open(filepath + tokens[1],'rb') as f:
                    bytes_to_read = 1024
                    file_data=f.read(bytes_to_read)
                    while file_data:
                        s.sendall(file_data)
                        file_data=f.read(bytes_to_read)


                data = s.recv(1024).decode("utf-8")
                if (data.split(delimiter)[0]=='1'):
                    print("File Received!")
                else:
                    print(data.split(delimiter)[1])
                s.close()

            elif (tokens[0].upper()=="LIST"):                            #LIST  FORMAT PDF
                if len(tokens) != 1:
                    print("Invalid args to <list>")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr, self.load_bal_port))
                padded_msg="LIST"+delimiter+"groups"+delimiter+self.username      #LIST@groups@user1- FORMAT SERVER
                s.send(padded_msg.encode('utf-8'))         
                data = s.recv(1024).decode("utf-8")                 # 1@grpname@num_users@grpname@num
                if (data.split(delimiter)[0]=='1'):
                    grps_list=data[2:].split(delimiter)
                    for i in range(0,len(grps_list),2):
                        print(grps_list[i]," : ",grps_list[i+1])                                  
                else:
                    print(data.split(delimiter)[1])
                s.close()
            
            elif (tokens[0].upper()=="JOIN"):                           #JOIN g1-FORMAT PDF
                if len(tokens) != 2:
                    print("Invalid args to <join>")
                    continue
                if tokens[1] in self.groupkeys.keys():
                    print("You are already a member of the group")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr,self.load_bal_port))
                padded_msg="JOIN"+delimiter+tokens[1]+delimiter+self.username                   
                s.send(padded_msg.encode('utf-8'))          #JOIN@group1@user2 -FORMAT SERVER
                data = s.recv(1024).decode("utf-8")         # 1@grp_key
                if (data.split(delimiter)[0]=='1'):
                    print("Group Joined! ")
                    # print(data.split(delimiter)[1])        # server returns key of that group
                    self.groupkeys[tokens[1]] = data.split(delimiter)[1]
                else:
                     print(data.split(delimiter)[1])
                s.close()
            
            elif (tokens[0].upper()=="CREATE"):             #create g1 FORMAT PDF
                if len(tokens) != 2:
                    print("Invalid args to <create>")
                    continue
                if tokens[1] in self.groupkeys.keys():
                    print("You are already a member of the group")
                    continue      
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr,self.load_bal_port))
                padded_msg="CREATE"+delimiter+tokens[1]+delimiter+self.username        
                s.send(padded_msg.encode('utf-8'))                   #CREATE@group1@user1 -FORMAT SERVER 
                data = s.recv(1024).decode("utf-8")
                if (data.split(delimiter)[0]=='1'):               #1@group_created@randomkey
                    print("Group Created! ")
                    self.groupkeys[tokens[1]] = data.split(delimiter)[2]
                else:
                    print(data.split(delimiter)[1])
                s.close()
            elif (tokens[0].upper() == "SHOW_GROUPS"):
                self.show_my_groups()
            # else:
            #     print("Invalid Command")


def main():
    if len(sys.argv) != 3:
        print("Type in the format : client.py <client_PORT> <load_balancer_port>")
        return
    #---Listening for other clients or servers
    client_IP = "127.0.0.1"
    client_PORT = sys.argv[1]
    print("Listening on ",client_IP,client_PORT)

    thisUser = User(sys.argv[2])
    
    initial_thread = threading.Thread(target = thisUser.client_as_server, args=(client_IP, client_PORT))
    initial_thread.start()

    print("\nWelcome !!")
    print("New User?   Sign up <Name> <Roll no.> <Password>")
    print("Already have an account?   Login <Name||Roll no.> <Password>\n")
    while True:
        org_msg=input(":")
        # padded_msg=appending_dollar(org_msg)+client_IP+"@"+client_PORT
        tokens=org_msg.split(' ')
        # print(tokens)
        if tokens[0] == '':
            continue
        signup_check=tokens[0].lower()+" "+tokens[1].lower()
        if (signup_check=="sign up"):                        #SIGN UP U1 R1 P1  #Indx-0 1 2 3 4 #LEN-5
            if len(tokens) != 5:
                print("Invalid args to <Signup>")
                continue
            #---Connecting to Load Balancer                        
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((thisUser.load_bal_Addr,thisUser.load_bal_port))
            # print(s.getsockname()[1])
            username = tokens[2]+tokens[3]                                             
            padded_msg="SIGN"+delimiter+"UP"+delimiter+username+delimiter+tokens[4]+delimiter+client_IP+delimiter+client_PORT
            s.send(padded_msg.encode('utf-8'))                          #SIGN@UP@U1R1@P1@IP@PORT
            data = s.recv(1024).decode("utf-8") 
            print("data recv = ",data)
            if (data.split(delimiter)[0]=='1'):
                print("Successfully SIGNED UP!")
            else:
                print("Sign up Failed! Try Again")
            s.close()
        
        elif (tokens[0].lower()=="login"):                              #login username passwd
            if len(tokens) != 3:
                print("Invalid args to <Login>")
                continue            
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print(s.getsockname()[1])
            s.connect((thisUser.load_bal_Addr,thisUser.load_bal_port))
            padded_msg = "SIGN"+delimiter+"IN"+delimiter+tokens[1]+delimiter+tokens[2]+delimiter+client_IP+delimiter+client_PORT   #SIGN@IN@U1@P1
            # print(""padded_msg)
            s.send(padded_msg.encode('utf-8'))
            data = s.recv(1024).decode("utf-8")
            print("data = ",data)
            if (data.split(delimiter)[0]=='1'):
                print("Successfully LOGGED IN!")
                thisUser.set_username(tokens[1])
                grps_info = data.split(delimiter)
                if len(grps_info) > 2:
                    for i in range(1,len(grps_info),2):
                        thisUser.groupkeys[grps_info[i]] = grps_info[i+1]
                thisUser.show_my_groups()
                thisUser.interact_with_server()
                break
            else:
                print(data.split(delimiter)[1])
            s.close()
        else:
            print("Please signup/login first!")


if __name__ == '__main__':
    main()