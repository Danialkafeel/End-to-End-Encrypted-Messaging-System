import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
port = 60000
#port = 50000

#url = "GET site1/Lab1.pdf"
url = input("Enter the Url\n")
filepath = url.split(' ')[1].split('/')[1]
#print(filepath)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, port))
    s.sendall(url.encode('utf-8'))
    message = s.recv(1024).decode("utf-8")
    if(message == "File not Present"):
        print(message)
        s.close()
        exit()
    else:
        file_ptr = open(filepath, 'wb')
        data = s.recv(1024)
        while data:
            file_ptr.write(data)
            data = s.recv(1024)
    file_ptr.close()
    print("The socket is closed now")
    s.close()
