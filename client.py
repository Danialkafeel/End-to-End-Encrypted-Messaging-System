import threading, socket, os
import sys, hashlib
<<<<<<< HEAD

class User(object):
    def __init__(self, load_port):
        self.load_bal_Addr= "127.0.0.1"
        self.load_bal_port= int(load_port)
        self.username = ""
        self.isLoggedIn = False
        self.groupkeys = dict()   # grp name -> keys map
        # self.q = FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF
        # 2410312426921032588552076022197566074856950548502459942654116941958108831682612228890093858261341614673227141477904012196503648957050582631942730706805009223062734745341073406696246014589361659774041027169249453200378729434170325843778659198143763193776859869524088940195577346119843545301547043747207749969763750084308926339295559968882457872412993810129130294592999947926365264059284647209730384947211681434464714438488520940127459844288859336526896320919633919
=======
load_bal_Addr="127.0.0.1"
load_bal_port=9999

class User(object):
    def __init__(self):
        self.username = ""
        self.isLoggedIn = False
        self.groupkeys = dict()   # grp name -> keys map
      #   self.q = FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
      # 29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
      # EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
      # E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
      # EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
      # C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
      # 83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
      # 670C354E 4ABC9804 F1746C08 CA237327 FFFFFFFF FFFFFFFF
>>>>>>> ec1c26d4bbedabe24c5c666834e795c4a0b6b33a
        self.alpha = 2

    def set_username(self,usern):
        self.username = usern

    def join_group(self,groupname,key):
        groupkeys[groupname] = key

    def handle_request(self,connection):        ## DHK recv side
        data = connection.recv(1024)    ##  Assume this to be public key of sender
        message = data.decode("utf-8")
        message = message.split(' ')[1]
        filepath = '.' + '/' + message
        if(os.path.isfile(filepath)):
            message = "Sending file"
            connection.sendall(message.encode("utf-8"))

            file_ptr = open(filepath, "rb")
            bytes_read = file_ptr.read(1024)
            while(bytes_read):
                connection.send(bytes_read)
                bytes_read = file_ptr.read(1024)
        else:
            message = "File not Present"
            connection.sendall(message.encode("utf-8"))
        print("Connection is closed")
        connection.close()
        return

    def client_as_server(self,host_addr, port):             ##      Receiver of msg
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host_addr, int(port)))

        thread_list=[]
        while True:
            s.listen()
            conn, addr = s.accept()
            thread = threading.Thread(target = handle_request, args= (self,conn, ))
            thread_list.append(thread)
            thread.start()

    def client_connection_with_other_client(self,ip,port, msg):     ## Sender of msg
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,port))
        ##      Implement DHK sender side here!
        user = str(rand()%1000)+srt(self.username)
        private_key = hashlib.sha256(user.encode())



        s.send(padded_msg.encode('ascii'))
        data = s.recv(1024).decode("utf-8")
        print(data)

    def interact_with_server(self):
        print("Send <Name||Roll no.> <message>")    # 4 ways
        print("Send_group <No. of groups> <Group no.(s)> <message>")    # 4 ways    send_group 2 g1 g2 this is my g2 dsjfkdlsajfkl
        print("List")
        print("Create <Group name>")
        print("Join <Group name>\n")
        while True:
            org_msg=input(":")
            # padded_msg=appending_dollar(org_msg)+client_IP+"$"+client_PORT
            tokens=org_msg.split(' ')
            if (tokens[0].lower()=="send"):     
                if len(tokens) <  3:
                    print("Invalid args to <send>")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
<<<<<<< HEAD
                s.connect((self.load_bal_Addr,self.load_bal_port))
=======
                s.connect((load_bal_Addr,load_bal_port))
>>>>>>> ec1c26d4bbedabe24c5c666834e795c4a0b6b33a

                padded_msg = "send$"+tokens[1]          # send$username_of_recv$username_of_sender
                s.send(padded_msg.encode('utf-8'))
                data = s.recv(1024).decode("utf-8")     #  1$IP$PORT of receiver.
                if (data.split('$')[0]=='1'):
                    recv_ip=data.split('$')[1]
                    recv_port=data.split('$')[2]
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (self,recv_ip,recv_port,tokens[2])) 
                    thread_list.append(thread)
                    thread.start()
                    #---IMP! Yaha check krlo kch sahe krna ho ya add krna ho...not sure about this part
                else:
                    print(data.split('$')[1])
            elif (tokens[0].lower()=="send_group"):     
                if len(tokens) <  4:
                    print("Invalid args to <send_group>")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
<<<<<<< HEAD
                s.connect((self.load_bal_Addr,self.load_bal_port))
=======
                s.connect((load_bal_Addr,load_bal_port))
>>>>>>> ec1c26d4bbedabe24c5c666834e795c4a0b6b33a

                padded_msg = "send_group$"+tokens[1]          # send_group$username_of_recv$username_of_sender
                s.send(padded_msg.encode('utf-8'))
                data = s.recv(1024).decode("utf-8")     #  1$IP$PORT of receiver.
                if (data.split('$')[0]=='1'):
                    recv_ip=data.split('$')[1]
                    recv_port=data.split('$')[2]
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (self,recv_ip,recv_port,tokens[2])) 
                    thread_list.append(thread)
                    thread.start()
                    #---IMP! Yaha check krlo kch sahe krna ho ya add krna ho...not sure about this part
                else:
                    print(data.split('$')[1])
            
            elif (tokens[0]=="LIST"):
                s.send(padded_msg.encode('ascii'))
                data = s.recv(1024).decode("utf-8")
                if (data.split('$')[0]==1):
                    for i in data.split('$')[0][1]:         #Assuming ke 2nd token from serve is a list jisme naam honge
                        print(i)                                    # groups ke
                else:
                    print("No Group")
            
            elif (tokens[0]=="JOIN"):
                s.send(padded_msg.encode('ascii'))
                data = s.recv(1024).decode("utf-8")
                if (data.split('$')[0]==1):
                    print("Joined Successfully")        # server returns key of that group

                else:
                     print("Group not Present")
            
            elif (tokens[0]=="CREATE"):
                s.send(padded_msg.encode('ascii'))
                data = s.recv(1024).decode("utf-8")
                if (data.split('$')[0]==1):
                    print("Created Successfully")
                else:
                    print("Group Already Present! Try Again")
            else:
                print("Invalid Command")

def appending_dollar(msg):
    s=""
    for i in msg.split(' '):
        s += i.strip()+"$"
    return s

def main():
    if len(sys.argv) != 3:
<<<<<<< HEAD
        print("Type in the format : client.py <client_PORT> <load_bal_port>")
        return
    #---Listening for other clients or servers
    client_IP = "127.0.0.1"
    client_PORT = sys.argv[1]
    print("Listening on ",client_IP,client_PORT)

    thisUser = User(sys.argv[2])
=======
        print("Type in the format : client.py <IP> <PORT>")
        return
    #---Listening for other clients or servers
    client_IP = sys.argv[1]
    client_PORT = sys.argv[2]
    print("Listening on ",client_IP,client_PORT)

    thisUser = User()
>>>>>>> ec1c26d4bbedabe24c5c666834e795c4a0b6b33a
    
    initial_thread = threading.Thread(target = thisUser.client_as_server, args=(client_IP, client_PORT))

    print("Available Commands")
    print("Signup <Name> <Roll no.> <Password>")
    print("Login <Name||Roll no.> <Password>\n")
    while True:
        org_msg=input(":")
        # padded_msg=appending_dollar(org_msg)+client_IP+"$"+client_PORT
        tokens=org_msg.split(' ')
        
        if (tokens[0].lower()=="signup"):
            if len(tokens) != 4:
                print("Invalid args to <Signup>")
                continue
            #---Connecting to Load Balancer
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
<<<<<<< HEAD
            s.connect((thisUser.load_bal_Addr,thisUser.load_bal_port))
=======
            s.connect((load_bal_Addr,load_bal_port))
>>>>>>> ec1c26d4bbedabe24c5c666834e795c4a0b6b33a
            # print(s.getsockname()[1])
            username = tokens[1]+tokens[2]
            padded_msg = "signup$"+username+"$"+tokens[3]
            s.send(padded_msg.encode('utf-8'))
            data = s.recv(1024).decode("utf-8") 
<<<<<<< HEAD
            if (data.split('$')[0]=='1'):
=======
            if (data.split('$')[0]==1):
>>>>>>> ec1c26d4bbedabe24c5c666834e795c4a0b6b33a
                print("Sign up Successful!")
            else:
                print("Sign up Failed! Try Again")
            s.close()
        
        elif (tokens[0].lower()=="login"):
            if len(tokens) != 3:
                print("Invalid args to <Login>")
                continue            
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(s.getsockname()[1])
<<<<<<< HEAD
            s.connect((thisUser.load_bal_Addr,thisUser.load_bal_port))
=======
            s.connect((load_bal_Addr,load_bal_port))
>>>>>>> ec1c26d4bbedabe24c5c666834e795c4a0b6b33a
            padded_msg = "login$"+tokens[1]+"$"+tokens[2]
            s.send(padded_msg.encode('utf-8'))
            data = s.recv(1024).decode("utf-8") 
            if (data.split('$')[0]=='1'):
                print("Login in Successful!")
                s.close()
                thisUser.set_username(token[1])
                ####                Add grps name+keys on login
                thisUser.interact_with_server()
                break
            else:
                print(data.split('$')[1])
        else:
            print("Please signup/login first!")

if __name__ == '__main__':
    main()