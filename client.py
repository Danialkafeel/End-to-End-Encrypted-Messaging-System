import threading, socket, os
import sys
load_bal_Addr="127.0.0.1"
load_bal_port=9999
isLoggedIn = False

def appending_dollar(msg):
    s=""
    for i in msg.split(' '):
        s += i.strip()+"$"
    return s

def handle_request(connection):
    data = connection.recv(1024)
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




def client_as_server(host_addr, port):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host_addr, int(port)))

    thread_list=[]
    while True:
        s.listen()
        conn, addr = s.accept()
        thread = threading.Thread(target = handle_request, args= (conn, ))
        thread_list.append(thread)
        thread.start()





def client_connection_with_other_client(ip,port):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip,port))
    while true:
        msg=input()
        s.send(padded_msg.encode('ascii'))
        data = s.recv(1024).decode("utf-8")
        print(data)


def main():
    if len(sys.argv) != 3:
        print("Type in the format : client.py <IP> <PORT>")
        return
    #---Listening for other clients or servers
    client_IP = sys.argv[1]
    client_PORT = sys.argv[2]
    print("Listening on ",client_IP,client_PORT)
    
    initial_thread = threading.Thread(target = client_as_server, args=(client_IP, client_PORT))

    #---Connecting to Load Balancer
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((load_bal_Addr,load_bal_port))

    #---Ek Ackn daal sakte hai from Load Balancer after connection with Load Balancer le Welcome ya kch bhe
    print("Available Commands")
    print("Signup <Name> <Roll no.> <Password>")
    print("Login <Name||Roll no.> <Password>")
    print("Send <Name||Roll no.> <message>")
    print("List")
    print("Create <Group name>")
    print("Join <Group name>\n")
    while True:
        org_msg=input(":")
        # padded_msg=appending_dollar(org_msg)+client_IP+"$"+client_PORT
        tokens=org_msg.split(' ')
        
        if (tokens[0].lower()=="signup"):
            if len(tokens) != 4:
                print("Invalid args to <Signup>")
                continue
            username = tokens[1]+tokens[2]
            padded_msg = "signup$"+username+"$"+tokens[3]
            s.send(padded_msg.encode('ascii'))
            data = s.recv(1024).decode("ascii") 
            if (data.split('$')[0]==1):
                print("Sign up Successful! ")
            else:
                print("Sign up Failed! Try Again")
        
        elif (tokens[0].lower()=="login"):
            if len(tokens) != 3:
                print("Invalid args to <Login>")
                continue            
            padded_msg = "login$"+tokens[1]+"$"+tokens[2]
            s.send(padded_msg.encode('ascii'))
            data = s.recv(1024).decode("utf-8") 
            if (data.split('$')[0]==1):
                print("Login in Successful! ")
            else:
                print("Wrong Credentianals or Sign Up First")

        elif (tokens[0].lower()=="send"):
            s.send(padded_msg.encode('ascii'))
            data = s.recv(1024).decode("utf-8")
            if (data.split('$')[0]==1):
                recv_ip=data.split('$')[-2]
                recv_port=data.split('$')[-1]
                thread = threading.Thread(target = client_connection_with_other_client, args= (recv_ip,recv_port)) 
                thread_list.append(thread)
                thread.start()
                #---IMP! Yaha check krlo kch sahe krna ho ya add krna ho...not sure about this part
            else:
                print("USERNAME Not Present or Login or Sign up First")
        
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
                print("Joined Successfully")
            else:
                 print("Group not Present")
        
        elif (tokens[0]=="CREATE"):
            s.send(padded_msg.encode('ascii'))
            data = s.recv(1024).decode("utf-8")
            if (data.split('$')[0]==1):
                print("Created Successfully")
            else:
                print("Group Already Present! Try Again")
        
        padded_msg=""
        #Session End ka bhe kch msg daal sakte hai quit ya kch bhe

if __name__ == '__main__':
    main()