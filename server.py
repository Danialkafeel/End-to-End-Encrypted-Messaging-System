import os, sqlite3, json
import re, random
import threading, socket
from threading import Lock
from time import sleep

database_path = "./MyDatabase.db"
json_file_path = "./queries.json"
path_to_store_files = "./Debug/"
delimiter = '@'
MAX_NUM_THREADS = 3
I_AM_BUSY = False

def generate_random_key():
    value = random.randint(100000000000000000000000, 999999999999999999999999)
    return str(value)

def add_quotes(string):
    return "'" + string + "'"

def IfExists(string1, string2):
    search_result =  re.search(string1, string2, re.IGNORECASE)
    return search_result

def IsAccountExist(data, username):
    query_to_execute = data['queries']['get_column'].format("Username", "User")
    usernames = execute_query(query_to_execute)
    usernames = [user[0] for user in usernames]
    return (username in usernames)
    # return IfExists(username, usernames)

def IsPasswordExist(data, username, password):
    query_to_execute = data['queries']['get_column_conditional_query'].format("password", "User", "Username = {}".format(add_quotes(username)))
    password_fetched = execute_query(query_to_execute)
    password_fetched = password_fetched[0][0]
    return password == password_fetched
    # return IfExists(password, passwords)

def IsSignedIn(data, username):
    query_to_execute = data['queries']['get_column_conditional_query'].format("IsSignedIn", "User", "Username = {}".format(add_quotes(username)))
    status = execute_query(query_to_execute)
    return status[0][0] == '1'

def IsGroupExist(data, group):
    query_to_execute = data['queries']['get_column'].format("Groupname", "Group_info")
    groups = execute_query(query_to_execute)
    groups = ' '.join([group[0] for group in groups])
    
    return IfExists(group, groups)

def execute_query(query):
    # connecting to the database 
    connection = sqlite3.connect(database_path)
    
    #cursor
    crsr = connection.cursor()
    
    query_result = ""
    try:
        # execute the statement 
        crsr.execute(query)
        query_result = crsr.fetchall() 
    except Exception as e:
        print(e)
    
    # If we skip this, nothing will be saved in the database. 
    connection.commit() 
    
    # close the connection 
    connection.close()

    return query_result

def send_group_message(data, message, group, members, index, max_number_threads):
    message = '3' + delimiter + group + delimiter+ message
    while(index < len(members)):
        peer = members[index]
        #get ip of peer
        query_to_execute = data['queries']['get_column_conditional_query'].format("ip", "User", "Username = {}".format(add_quotes(peer)))
        ip = execute_query(query_to_execute)
        ip = ip[0][0]

        #get port of peer
        query_to_execute = data['queries']['get_column_conditional_query'].format("port", "User", "Username = {}".format(add_quotes(peer)))
        port = execute_query(query_to_execute)
        port = port[0][0]
        
        #Connect with client and send him the message
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            s.connect( (ip ,int(port)) )
            s.sendall(message.encode("UTF-8"))
        except Exception as e:
            print(e)

        s.close()
        index += max_number_threads
    
    return

def send_group_file(data, group, filename, filepath, members, index, max_number_threads):
    message = '4' + delimiter + filename + delimiter + group
    while(index < len(members)):
        peer = members[index]
        #get ip of peer
        query_to_execute = data['queries']['get_column_conditional_query'].format("ip", "User", "Username = {}".format(add_quotes(peer)))
        ip = execute_query(query_to_execute)
        ip = ip[0][0]

        #get port of peer
        query_to_execute = data['queries']['get_column_conditional_query'].format("port", "User", "Username = {}".format(add_quotes(peer)))
        port = execute_query(query_to_execute)
        port = port[0][0]
        
        #Connect with client and send him the message
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("message = ",message)
        print("ip, port ",ip,port)
        s.connect( (ip ,int(port)) )

        s.sendall(message.encode('utf-8'))
        sleep(.4)
        
        with open(filepath, 'rb') as fp:
            try:
                #offset = 0
                bytes_to_read = 1024
                file_data = fp.read(bytes_to_read)
                while file_data:
                    s.sendall(file_data)
                    #offset += bytes_to_read
                    file_data = fp.read(bytes_to_read)
            
            except Exception as e:
                print(e)
                
        s.close()
        index += max_number_threads
    
    return

def parse_message(connection, data, message):
    #get username of person sending request
    username = message.split(delimiter)[2]
    
    if IfExists('SIGN' + delimiter + 'UP', message):
        if IsAccountExist(data, username):
            return '0' + delimiter + 'Username already exists'
        else:
            password = message.split(delimiter)[3]
            ip = message.split(delimiter)[4]
            port = message.split(delimiter)[5]
            values = add_quotes(username) + ',' + add_quotes(password) + ',' +  add_quotes(ip) + ',' + add_quotes(port)  + ',' + "'1'" + ',' + "'-'"
            query_to_execute = data['queries']['insert_into'].format("User", values)
            execute_query(query_to_execute)

            ###Update query, change the signed in column status
            query_to_execute = data['queries']['update_query'].format("User", "IsSignedIn = '1'", "Username = {}".format(add_quotes(username)))
            execute_query(query_to_execute)

            return '1' + delimiter + 'Your account has been made'
    else:
        if IfExists("SIGN" + delimiter + "IN", message):
            password = message.split(delimiter)[3]
            ip = message.split(delimiter)[4]
            port = message.split(delimiter)[5]
            if not IsAccountExist(data,username):
                return '0' + delimiter + 'Username is incorrect'
            
            if not IsPasswordExist(data, username, password):
                return '0' + delimiter + 'Password is incorrect'
    
            # Update query, change the signed in column status
            query_to_execute = data['queries']['update_query'].format("User", "IsSignedIn = '1'", "Username = {}".format(add_quotes(username)))
            execute_query(query_to_execute)

            # Update the ip
            query_to_execute = data['queries']['update_query'].format("User", "ip = {}".format(add_quotes(ip)), "Username = {}".format(add_quotes(username)))
            execute_query(query_to_execute)

            # Update the port
            query_to_execute = data['queries']['update_query'].format("User", "port = {}".format(add_quotes(port)), "Username = {}".format(add_quotes(username)))
            execute_query(query_to_execute)

            # Send the random keys of groups user is part of
            query_to_execute = data['queries']['get_column_conditional_query'].format("PartofGroups", "User", "Username = {}".format(add_quotes(username)))
            part_of_groups = execute_query(query_to_execute)
            # print(part_of_groups)
            part_of_groups = part_of_groups[0][0].split(delimiter)

            ans_str = ''
            for group in part_of_groups:
                if(group == '-'):
                    continue
                query_to_execute = data['queries']['get_column_conditional_query'].format("randomkey", 'Group_info', "Groupname = {}".format(add_quotes(group)))
                randomkey = execute_query(query_to_execute)
                randomkey = randomkey[0][0]
                ans_str = ans_str + delimiter + group + delimiter + randomkey 

            return '1' + (delimiter if ans_str == '' else ans_str)

        elif( IfExists("SEND", message) and not IfExists("SEND_GROUP", message)):
            peer_name = message.split(delimiter)[3]
            if not IsAccountExist(data, username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(data, username):
                return '0' + delimiter + 'You are not Signed in'

            if not IsAccountExist(data, peer_name):
                return '0' + delimiter + 'Peer which you are sending message to doesnt exist'
            
            #Get ip of peer
            query_to_execute = data['queries']['get_column_conditional_query'].format("ip", "User", "Username = {}".format(add_quotes(peer_name)))
            ip = execute_query(query_to_execute)
            ip = ip[0][0]

            #get port number of peer
            query_to_execute = data['queries']['get_column_conditional_query'].format("port", "User", "Username = {}".format(add_quotes(peer_name)))
            port = execute_query(query_to_execute)
            port = port[0][0]

            return '1' + delimiter + ip + delimiter + port
        
        elif IfExists("LIST", message):
            if not IsAccountExist(data, username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(data, username):
                return '0' + delimiter + 'You are not Signed in'

            #get list of groups
            query_to_execute = data['queries']['get_column'].format("Groupname", "Group_info")
            groups = execute_query(query_to_execute)

            #get list of members in groups
            ans_string = ''
            for index,group in enumerate(groups):
                group_name = groups[index][0]
                query_to_execute = data['queries']['get_column_conditional_query'].format("members", "Group_info", "Groupname = {}".format(add_quotes(group_name)))
                members = execute_query(query_to_execute)
                members = members[0][0]
                ans_string = ans_string + delimiter + group_name + delimiter + str(len(members.split(delimiter)))

            #Pay attention here
            return '1' + ans_string
        
        elif IfExists("CREATE", message):
            group = message.split(delimiter)[1]
            if not IsAccountExist(data, username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(data, username):
                return '0' + delimiter + 'You are not Signed in'
            
            if IsGroupExist(data, group):
                return '0' + delimiter + 'A group with this name already exists'
            
            #Update entry for user in the user table in PartofGroupsColumn
            query_to_execute = data['queries']['get_column_conditional_query'].format("PartofGroups", "User", "Username = {}".format(add_quotes(username)) )
            part_of_groups = execute_query(query_to_execute)
            part_of_groups = part_of_groups[0][0]
            if(part_of_groups == '-'):
                part_of_groups = group
            else:
                part_of_groups = part_of_groups + delimiter + group
            
            query_to_execute = data['queries']['update_query'].format("User", "PartofGroups = {}".format(add_quotes(part_of_groups)), "Username = {}".format(add_quotes(username)))
            execute_query(query_to_execute)

            #Create entry in the group table
            randomkey = generate_random_key()
            members = username
            query_to_execute = data['queries']['insert_into'].format("Group_info", add_quotes(group) + ',' + add_quotes(members) + ',' + add_quotes(randomkey))
            execute_query(query_to_execute)

            return '1' + delimiter + "Group created" + delimiter + str(randomkey)

        elif IfExists("JOIN", message):
            group = message.split(delimiter)[1]
            if not IsAccountExist(data, username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(data,username):
                return '0' + delimiter + 'You are not Signed in'
            
            if not IsGroupExist(data,group):
                message = message.replace("JOIN", "CREATE")
                return parse_message(connection, data, message)
            
            #Update entry for user in the user table in PartofGroupsColumn
            query_to_execute = data['queries']['get_column_conditional_query'].format("PartofGroups", "User", "Username = {}".format(add_quotes(username)) )
            part_of_groups = execute_query(query_to_execute)
            part_of_groups = part_of_groups[0][0]
            if(part_of_groups == '-'):
                part_of_groups = group
            else:
                part_of_groups = part_of_groups + delimiter + group
            
            query_to_execute = data['queries']['update_query'].format("User", "PartofGroups = {}".format(add_quotes(part_of_groups)), "Username = {}".format(add_quotes(username)))
            execute_query(query_to_execute)

            ####Update group members####
            query_to_execute = data['queries']['get_column_conditional_query'].format('members', 'Group_info', 'Groupname = {}'.format(add_quotes(group)))
            group_members = execute_query(query_to_execute)
            group_members = group_members[0][0]
            group_members = group_members + delimiter + username
            query_to_execute = data['queries']['update_query'].format("Group_info", "members = {}".format(add_quotes(group_members)), "Groupname = {}".format(add_quotes(group)))
            execute_query(query_to_execute)

            ##Get random key of group
            query_to_execute = data['queries']['get_column_conditional_query'].format('randomkey', 'Group_info', 'Groupname = {}'.format(add_quotes(group)))
            randomkey = execute_query(query_to_execute)
            randomkey = randomkey[0][0]
            
            return '1' + delimiter + randomkey

        elif IfExists("SEND_GROUP", message) and IfExists("DUMMY", message):       #   SEND_GROUP$DUMMY$USERNAME$message$G1$G2$G3
            message_to_send = message.split(delimiter)[3]

            #Iterate through each group one by one and send messages to the members
            for group_index in range(4, len(message.split(delimiter))):
                group = message.split(delimiter)[group_index]
            
                #get all the members in the group
                query_to_execute = data['queries']['get_column_conditional_query'].format('members', 'Group_info', "Groupname = {}".format(add_quotes(group)))
                members = execute_query(query_to_execute)
                members = members[0][0].split(delimiter)
                if username not in members:
                    return '0' + delimiter + 'You are not part of the group'
                
                #Remove yourself from the members list
                members.remove(username)
                num_members = len(members)

                #if You were the only person in the group
                if num_members == 0:
                    return '1'
                
                mutex = Lock()
                mutex.acquire()
                I_AM_BUSY = True
                mutex.release()

                #Create threads and send the messages
                index = 0
                for _ in range(min(MAX_NUM_THREADS, num_members)):
                    thread = threading.Thread(target = send_group_message, args = (data, message_to_send, group, members, index, MAX_NUM_THREADS,))
                    index += 1
                    thread.start()
                
                
                mutex.acquire()
                I_AM_BUSY = False
                mutex.release()
            
            return '1'

        elif IfExists("SEND_GROUP_FILE", message):
            filename = message.split(delimiter)[1]
            
            #Store the file in your local directory
            filepath = path_to_store_files + filename
            with open(filepath, 'wb') as f:
                file_data = connection.recv(1024)
                while file_data:
                    f.write(file_data)
                    file_data = connection.recv(1024)
            
            #After writing the file, close the connection with the load balancer
            #connection.sendall('1')
            connection.close()
            
            #Make new connection with clients now
            #Iterate through each group one by one and send files to the members
            for group_index in range(3, len(message.split(delimiter))):
                group = message.split(delimiter)[group_index]
            
                #get all the members in the group
                query_to_execute = data['queries']['get_column_conditional_query'].format('members', 'Group_info', "Groupname = {}".format(add_quotes(group)))
                members = execute_query(query_to_execute)
                members = members[0][0].split(delimiter)
                if username not in members:
                    return '0' + delimiter + 'You are not part of the group'
                
                #Remove yourself from the members list
                members.remove(username)
                num_members = len(members)

                #if You were the only person in the group
                if num_members == 0:
                    return '1'
                
                mutex = Lock()
                mutex.acquire()
                I_AM_BUSY = True
                mutex.release()

                #Create threads and send the messages
                index = 0
                for _ in range(min(MAX_NUM_THREADS, num_members)):
                    thread = threading.Thread(target = send_group_file, args = (data, group, filename, filepath, members, index, MAX_NUM_THREADS,))
                    index += 1
                    thread.start()
                
                
                mutex.acquire()
                I_AM_BUSY = False
                mutex.release()
            
            return


            
def init_db():
    #Open the configuration json file
    with open(json_file_path) as f:
        ldata = json.load(f)

    if not os.path.isfile(database_path):
        for table_name in ldata['tables'].keys():
            query_to_execute = ldata["queries"]["create_table"]
            schema = " VARCHAR (20) ,".join(ldata["tables"][table_name]["schema"])
            query_to_execute = query_to_execute.format(table_name, schema)
            #print(query_to_execute)
            execute_query(query_to_execute)

    else:
        print("Database File already exists")
    
    
    return ldata


class Server():
    s = None
    port = None

    def __init__(self, port):
        
        self.port = port
        self.s = socket.socket()
        self.s.bind(('', self.port))
        file1 = open('ip.txt', 'a') 
        m = str(self.s.getsockname()[1])+"\n"
        print(self.s.getsockname()[1])
        self.port = self.s.getsockname()[1]
        file1.write(m) 
        file1.close()
        
       
        # Writing a string to file 
    def start(self,data):
        self.s.listen(5)
        
        while True:  
            # Establish connection with loadbalancer.  
            connection, addr = self.s.accept()      
            print ('Got connection from', addr ) 
            message = connection.recv(1024)
            message = message.decode('utf-8')
            print("Request is ", message)
            response_message = parse_message(connection, data, message)
            # print("respnse message")
            if response_message is not None:
                print("respnse ",response_message)  
                connection.send(response_message.encode("utf-8")) 
                # print("Message sent ") 

                # Close the connection with the client 
            try:
                connection.close()
            except Exception as e:
                print(e)
            
    
    def __del__(self):
        with open("ip.txt", "r") as f:
            lines = f.readlines()
        with open("ip.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != str(self.port):
                    f.write(line)

def main():
    #initialize the database and read from configuration file
    data = init_db()
    
    #Initialize the server
    se = Server(0)
    se.start(data)
    
if __name__ == '__main__':
    main()


    # messages = ["SIGN UP user1 pwd1 127.0.0.1 5000", "SIGN UP user2 pwd2 127.0.0.1 6000", "SIGN UP user1 pwd2 127.0.0.1 5000", "SEND DUMMY user1 user2",
    # "CREATE group1 user1 100", "CREATE group2 user2 200", "JOIN group1 user2", "JOIN group2 user1", "LIST groups user1"]
    #  messages = ["SIGN UP user1 pwd1 127.0.0.1 5000", "SIGN UP user2 pwd2 127.0.0.1 6000", "SIGN UP user3 pwd3 127.0.0.1 7000", 
    #  "SIGN UP user1 pwd2 127.0.0.1 5000", "SEND DUMMY user1 user2","CREATE group1 user1 100", "CREATE group2 user2 200", 
    #  "JOIN group1 user2", "JOIN group2 user1", "JOIN group1 user3", "JOIN group3 user3", "LIST groups user1", 
    # "SIGN IN user1 pwd1", "SIGN IN user2 pwd3", "SEND_GROUP group1 user1 Hi"]
