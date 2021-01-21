# An example script to connect to Google using socket  
# programming in Python  
import socket # for socket 
import threading 



class Server():

    def __init__(self, port):
        self.port = port
        
        s = socket.socket() 
        s.bind(('', self.port)) 
        
        
        file1 = open('ip.txt', 'a') 
        m = str(s.getsockname()[1])+"\n"
        print(s.getsockname()[1])
        file1.write(m) 
        file1.close()
  
        # Writing a string to file 
         
        s.listen(5) 

        while True:  
            # Establish connection with client.  
            c,addr = s.accept()      
            print ('Got connection from', addr ) 
            g = c.recv(1024)
            # send a thank you message to the client.  
            c.send('Thank you for connecting'.encode()) 
            print("Message sent ") 

            # Close the connection with the client  
            c.close()
            break

    


    
        



            
servers =[]
for i in range(2):
    se = Server(0)
    servers.append(se)
