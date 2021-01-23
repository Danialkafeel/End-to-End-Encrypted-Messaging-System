import threading, socket, os
import sys, hashlib

delimiter="@"
dummy=""
class User(object):
    def __init__(self, load_port):
        self.load_bal_Addr= "127.0.0.1"
        self.load_bal_port= int(load_port)
        self.username = ""
        self.isLoggedIn = False
        self.groupkeys = dict()   # grp name -> keys map
        # self.q = FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF
        # 2410312426921032588552076022197566074856950548502459942654116941958108831682612228890093858261341614673227141477904012196503648957050582631942730706805009223062734745341073406696246014589361659774041027169249453200378729434170325843778659198143763193776859869524088940195577346119843545301547043747207749969763750084308926339295559968882457872412993810129130294592999947926365264059284647209730384947211681434464714438488520940127459844288859336526896320919633919
        self.alpha = 2

    def set_username(self,usern):
        self.username = usern

    def join_group(self,groupname,key):
        groupkeys[groupname] = key

    def handle_request(self,connection):        ## DHK recv side
        data = connection.recv(1024)    ##  Assume this to be public key of sender
        message = data.decode("utf-8")
        print("key received ",message)
        connection.send("my key is this.".encode('utf-8'))
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

        thread_list=[]
        while True:
            s.listen()
            conn, addr = s.accept()
            thread = threading.Thread(target = handle_request, args= (self,conn, ))
            thread_list.append(thread)
            thread.start()

    def client_connection_with_other_client(self,ip,port, msg):     ## Sender of msg
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,int(port)))
        ##      Implement DHK sender side here!
        user = str(rand()%1000)+srt(self.username)
        private_key = hashlib.sha256(user.encode())
        # public_key = self.alpha ^ private_key % self.q    # exp. to be implemented.
        public_key = "suppose key is generated."
        s.send(padded_msg.encode('utf-8'))
        data = s.recv(1024).decode("utf-8")
        print(data)

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

                padded_msg = "send"+dummy+delimiter+tokens[1]          # send@dummy@username_of_sender@username_of_recv
                s.send(padded_msg.encode('utf-8'))
                data = s.recv(1024).decode("utf-8")     #  1@IP@PORT of receiver.
                print("receiver details received",data)
                if (data.split(delimiter)[0]=='1'):
                    recv_ip=data.split(delimiter)[1]
                    recv_port=data.split(delimiter)[2]
                    thread = threading.Thread(target = self.client_connection_with_other_client, args= (recv_ip,recv_port,tokens[2])) 
                    thread.start()
                    #---IMP! 
                else:
                    print(data.split(delimiter)[1])
            elif (tokens[0].lower()=="send_group"):     
                if len(tokens) <  4:
                    print("Invalid args to <send_group>")
                    continue
                s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.load_bal_Addr,self.load_bal_port))

                padded_msg = "send_group"+delimiter+tokens[1]          # send_group@username_of_recv@username_of_sender
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
            
            elif (tokens[0]=="LIST"):
                s.send(padded_msg.encode('ascii'))      # LIST@dummy@username_sender
                data = s.recv(1024).decode("utf-8")     # 1@grpname@num_users@grpname.@num
                if (data.split(delimiter)[0]==1):
                    grps_list=t[2:].split(delimiter)
                    for i in range(0,len(grps_list),2):
                        print(grps_list[i]," : ",grps_list[i+1])                                  
                else:
                    print(data.split(delimiter)[1])
            
            elif (tokens[0]=="JOIN"):
                s.send(padded_msg.encode('ascii'))      # JOIN@grpname@username
                data = s.recv(1024).decode("utf-8")     # 1@grp_key
                if (data.split(delimiter)[0]==1):
                    print(data.split(delimiter)[1])        # server returns key of that group

                else:
                     print(data.split(delimiter)[1])
            
            elif (tokens[0]=="CREATE"):
                s.send(padded_msg.encode('ascii'))
                data = s.recv(1024).decode("utf-8")
                if (data.split(delimiter)[0]==1):
                    print(data.split(delimiter)[1])
                else:
                    print(data.split(delimiter)[1])
            else:
                print("Invalid Command")

def appending_dollar(msg):
    s=""
    for i in msg.split(' '):
        s += i.strip()+delimiter
    return s

def main():
    if len(sys.argv) != 3:
        print("Type in the format : client.py <client_PORT> <load_bal_port>")
        return
    #---Listening for other clients or servers
    client_IP = "127.0.0.1"
    client_PORT = sys.argv[1]
    print("Listening on ",client_IP,client_PORT)

    thisUser = User(sys.argv[2])
    
    initial_thread = threading.Thread(target = thisUser.client_as_server, args=(client_IP, client_PORT))

    print("\nWelcome !!")
    print("New User?   Signup <Name> <Roll no.> <Password>")
    print("Already have an account?   Login <Name||Roll no.> <Password>\n")
    while True:
        org_msg=input(":")
        # padded_msg=appending_dollar(org_msg)+client_IP+"@"+client_PORT
        tokens=org_msg.split(' ')
        
        if (tokens[0].lower()=="signup"):
            if len(tokens) != 4:
                print("Invalid args to <Signup>")
                continue
            #---Connecting to Load Balancer
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((thisUser.load_bal_Addr,thisUser.load_bal_port))
            # print(s.getsockname()[1])
            username = tokens[1]+tokens[2]
            padded_msg = "SIGN"+delimiter+"UP"+delimiter+username+delimiter+tokens[3]
            s.send(padded_msg.encode('utf-8'))
            data = s.recv(1024).decode("utf-8") 
            print("data recv = ",data)
            if (data.split(delimiter)[0]=='1'):
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
            s.connect((thisUser.load_bal_Addr,thisUser.load_bal_port))
            padded_msg = "sign"+delimiter"in"+delimiter+tokens[1]+delimiter+tokens[2]
            s.send(padded_msg.encode('utf-8'))
            data = s.recv(1024).decode("utf-8") 
            if (data.split(delimiter)[0]=='1'):
                print("Login in Successful!")
                s.close()
                thisUser.set_username(tokens[1])
                ####                Add grps name+keys on login
                thisUser.interact_with_server()
                break
            else:
                print(data.split(delimiter)[1])
        else:
            print("Please signup/login first!")

if __name__ == '__main__':
    main()