import threading, socket, os
import sys, hashlib
from random import randrange
import pyDes
import base64
from Crypto.Cipher import DES3

delimiter="@"

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
        groupkeys[groupname] = key
    def show_my_groups(self):
        for groupname in self.groupkeys.keys():
            print(groupname,":",self.groupkeys[groupname])

    def handle_request(self,connection):        ## DHK recv side
        data = connection.recv(1024)    ##  Assume this to be public key of sender
        #print("public_key of sender = ",data)
        user = str(randrange(1000)) + str(self.username)
        private_key = hashlib.sha256(user.encode())     # 32 Bytes no.
        public_key = pow(self.alpha, int(private_key.hexdigest(),16), self.q)
        #print("my public_key = ",public_key)
        connection.send(str(public_key).encode('utf-8'))
        shared_key = pow(int(data),int(private_key.hexdigest(),16),self.q) 
        #print("shared_key found ",shared_key)
        array2 = bytearray(str(shared_key), 'utf-16')
        #print(array2," ",type(array2)," ",len(array2))
        new_size=array2[-24:]
        #print(new_size," ",type(new_size)," ",len(new_size))
        cipher = DES3.new(new_size, DES3.MODE_CFB)
        data=connection.recv(1024)
        #print("Encypted data: ",data)
        decyrpted_msg=cipher.decrypt(data)
        print("Msg: ",decyrpted_msg.decode('utf-16')[4:])
        

        # message = message.split(' ')[1]
        # filepath = '.' + '/' + message
        # if(os.path.isfile(filepath)):
        #     message = "Sending file"
        #     connection.sendall(message.encode("utf-8"))

        #     file_ptr = open(filepath, "rb")
        #     bytes_read = file_ptr.read(1024)
        #     while(bytes_read):
        #         connection.send(bytes_read)
        #         bytes_read = file_ptr.read(1024)
        # else:
        #     message = "File not Present"
        #     connection.sendall(message.encode("utf-8"))
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

    def client_connection_with_other_client(self,ip,port, msg):     ## Sender of msg
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("ip, port = ",ip,port)
        s.connect((ip,int(port)))
        user = str(randrange(1000)) + str(self.username)                  #   Implement DHK sender side here!
        private_key = hashlib.sha256(user.encode())     # 32 Bytes no.
        public_key = pow(self.alpha, int(private_key.hexdigest(),16), self.q)
        #print("my public_key = ",public_key)
        s.send(str(public_key).encode('utf-8'))
        data = s.recv(1024).decode("utf-8")
        #print("public_key received = ",data)

        shared_key = pow(int(data),int(private_key.hexdigest(),16),self.q)
       
        array2 = bytearray(str(shared_key), 'utf-16')
        new_size=array2[-24:]

        print("OG ",msg)
        cipher = DES3.new(new_size, DES3.MODE_CFB)
        msg="GAR"+msg
        a=cipher.encrypt(msg.encode())
        #print("Encypted", type(a))
        s.send(cipher.encrypt(msg.encode('utf-16')))
        s.close()

    def interact_with_server(self):
        print("\nAvailable Commands")
        print("Send <Name||Roll no.> <message>")    # 4 ways
        print("Send_group <No. of groups> <Group no.(s)> <message>")    # 4 ways    send_group 2 g1 g2 this is my g2 dsjfkdlsajfkl
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
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (recv_ip,recv_port,msg)) 
                    thread.start()
                    #---IMP! 
                else:
                    print(data.split(delimiter)[1])

            elif (tokens[0].lower()=="send_group"):              #send_group grpname msg  FORMAT by pdf/us.
                if len(tokens) != 3:
                    print("Invalid args to <send_group>")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr,self.load_bal_port))
                #SEND_GROUP@group1@user1@msg FORMAT by server
                padded_msg = "SEND_GROUP"+delimiter+tokens[1]+delimiter+self.username+delimiter+tokens[2]          
                s.send(padded_msg.encode('utf-8'))
                data = s.recv(1024).decode("utf-8")    
                if (data.split(delimiter)[0]=='1'):
                    recv_ip=data.split(delimiter)[1]
                    recv_port=data.split(delimiter)[2]
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (recv_ip,recv_port,tokens[2])) 
                    thread_list.append(thread)
                    thread.start()
                    #---
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