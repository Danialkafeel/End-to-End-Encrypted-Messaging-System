import socket
import threading, sys
from _thread import *

delimiter = '@'

print_lock = threading.Lock()

class loadbalancer():
    modulus=0
    noofservers = 3
    message = ""
    semaphore = 1

    def __init__(self, port):
        self.port = int(port)
        s = socket.socket() 
        s.bind(('', self.port)) 
        print(s.getsockname()[1])
        s.listen(5)
            
        while True: 
            # establish connection with client 
            c, addr = s.accept() 
            #print_lock.acquire()
            print('Connected to :', addr[0], ':', addr[1]) 
    
            # Start a new thread and return its identifier 
            start_new_thread(self.threaded, (c,))

    def threaded(self, c): 
    
        # data received from client 
        data = c.recv(1024)
        print("data recv", data, "\n") 
        if data is None:
            c.close()
            return

        pno = self.get_and_update_port_number()
        pno = pno.strip('\n')
        print("pno = ",pno)
        val = self.make_connection_with_server(data, int(pno), c)
        
        c.send(val)
        
        # connection closed 
        c.close() 
    def make_connection_with_server(self, data, portno, socket_client):
        con = socket.socket()  
        # connect to the server on local computer 
        con.connect(('127.0.0.1', portno))  
        
        data2 = ''
        try:
            data2 = data.decode('utf-8')
        except Exception as e:
            print(e)

        if(data2.split(delimiter)[0] == 'SEND_GROUP_FILE'):
            print("Inside send_group_file condn ", data)
            con.send(data)
            file_data = socket_client.recv(1024)
            while(file_data):
                print("sending to server ",file_data)
                con.sendall(file_data)
                file_data = socket_client.recv(1024)
            
            val = con.recv(1024)
            print("val = ",val)
            return val
        
        else:
            #a = input("Type your message: ")
            con.send(data)
            # receive data from the server  
            val = con.recv(1024)
            # close the connection  
            con.close()  
        
        return val

    def get_and_update_port_number(self):
        f = open('ip.txt', 'r')
        lines = f.readlines()
        self.noofservers = len(lines)
        
        while not self.semaphore:
            pass
        self.semaphore = 0
        returnval = lines[self.modulus]
        self.modulus = (self.modulus+1) % self.noofservers
        self.semaphore = not self.semaphore
        self.semaphore = 1
        return returnval

def main():
    l = loadbalancer(sys.argv[1])

if __name__ == '__main__':
    main()