import threading, socket, os

host_addr = "127.0.0.1"
port = 9999
#port = 50000

message_format = "GET site1/Lab_1.pdf"

def get_filesize(filepath):
    stat = os.stat(filepath)
    return stat.st_size

def handle_request(connection):
    data = connection.recv(1024)
    message = data.decode("ascii")
    message = message.split('$')
    print(message)
    connection.send("yoo".encode("ascii"))
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
    # print("Connection is closed")
    connection.close()
    return

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host_addr, port))
    print('Listening on port ', port)

    while True:
        s.listen()
        conn, addr = s.accept()
        thread = threading.Thread(target = handle_request, args= (conn, ))
        thread.start()
        #thread.join()