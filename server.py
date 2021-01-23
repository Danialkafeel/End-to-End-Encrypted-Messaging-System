import os, sqlite3, json
import re, random
import threading, socket
from threading import Lock

database_path = "./MyDatabase.db"
json_file_path = "./queries.json"
delimiter = '@'
MAX_NUM_THREADS = 3
I_AM_BUSY = False


def generate_random_key():
    value = random.randint(10000000, 1000000000)
    return str(value)

def add_quotes(string):
    return "'" + string + "'"

def IfExists(string1, string2):
    return re.search(string1, string2, re.IGNORECASE)

def IsAccountExist(username):
    query_to_execute = data['queries']['get_column'].format("Username", "User")
    usernames = execute_query(query_to_execute)
    usernames = ' '.join([user[0] for user in usernames])
    return IfExists(username, usernames)

def IsPasswordExist(password):
    query_to_execute = data['queries']['get_column'].format("password", "User")
    passwords = execute_query(query_to_execute)
    passwords = ' '.join([password[0] for password in passwords])
    return IfExists(password, passwords)

def IsSignedIn(username):
    query_to_execute = data['queries']['get_column_conditional_query'].format("IsSignedIn", "User", "Username = {}".format(add_quotes(username)))
    status = execute_query(query_to_execute)
    
    return status[0][0] == '1'

def IsGroupExist(group):
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

def send_group_message(data, message, members, index, max_number_threads):
    while(max_number_threads < len(members)):
        peer = members[index]
        #get ip of peer
        query_to_execute = data['queries']['get_column_conditional_query'].format("ip", "User", "Username = {}".format(peer))
        ip = execute_query(query_to_execute)
        ip = ip[0][0]

        #get port of peer
        query_to_execute = data['queries']['get_column_conditional_query'].format("port", "User", "Username = {}".format(peer))
        port = execute_query(query_to_execute)
        port = ip[0][0]
        
        #Connect with client and send him the message
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(ip, port)

        try:
            s.send(message.encode("UTF-8"))
        except Exception as e:
            print(e)

        s.close()
        index += max_number_threads
    
    return

def parse_message(data, message):
    #get username of person sending request
    username = message.split(delimiter)[2]
    
    if IfExists('SIGN' + delimiter + 'UP', message):
        if IsAccountExist(username):
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
            if IsAccountExist(username):
                return '0' + delimiter + 'Username is incorrect'
            
            if IsPasswordExist(password):
                return '0' + delimiter + 'Password is incorrect'
    
            ###Update query, change the signed in column status
            query_to_execute = data['queries']['update_query'].format("User", "IsSignedIn = '1'", "Username = {}".format(username))
            execute_query(query_to_execute)

            ##Send the random keys of groups user is part of
            query_to_execute = data['queries']['get_column_conditional_query'].format("PartofGroups", "User", "Username = {}".format(add_quotes(username)))
            part_of_groups = execute_query(query_to_execute)
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

        elif IfExists("SEND", message):
            peer_name = message.split(delimiter)[3]
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(username):
                return '0' + delimiter + 'You are not Signed in'

            if not IsAccountExist(peer_name):
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
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(username):
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
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(username):
                return '0' + delimiter + 'You are not Signed in'
            
            if IsGroupExist(group):
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
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedIn(username):
                return '0' + delimiter + 'You are not Signed in'
            
            if not IsGroupExist(group):
                message = message.replace("JOIN", "CREATE")
                return parse_message(data, message)
            
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
            
            return '1' + delimiter + 'You have joined the group' + delimiter + randomkey

        elif IfExists("SEND_GROUP", message):
            group = message.split(delimiter)[1]
            
            #get all the members in the group
            query_to_execute = data['queries']['get_column_conditional_query'].format('members', 'Group_info', "Groupname = {}".format(add_quotes(group)))
            members = execute_query(query_to_execute)
            members = members[0][0].split(delimiter)
            if username not in members:
                return '0' + delimiter + 'You are not part of the group'
            
            members = members.remove(username)
            num_members = len(members)

            if num_members == 0:
                return '1'
            
            mutex = Lock()
            mutex.acquire()
            I_AM_BUSY = True
            mutex.release()

            #Create threads and send the messages
            index = 0
            for _ in range(min(MAX_NUM_THREADS, num_members)):
                threading.Thread(target = send_group_message, args = (data, message, members, index, MAX_NUM_THREADS,))
                index += 1
            
            
            mutex.acquire()
            I_AM_BUSY = False
            mutex.release()
            
            return '1'
            
def init_db():
    #Open the configuration json file
    with open(json_file_path) as f:
        data = json.load(f)

    if not os.path.isfile(database_path):
        for table_name in data['tables'].keys():
            query_to_execute = data["queries"]["create_table"]
            schema = " VARCHAR (20) ,".join(data["tables"][table_name]["schema"])
            query_to_execute = query_to_execute.format(table_name, schema)
            #print(query_to_execute)
            execute_query(query_to_execute)

    else:
        print("Database File already exists")
    
    return data


class Server():

    def __init__(self, port):
        data = init_db()
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
            message = c.recv(1024).decode('utf-8')
            response_message = parse_message(self.data, message)  
            c.send(response_message.encode("utf-8")) 
            print("Message sent ") 

            # Close the connection with the client  
            c.close()

def main():
    se = Server(0)
    
if __name__ == '__main__':
    main()



    # messages = ["SIGN UP user1 pwd1 127.0.0.1 5000", "SIGN UP user2 pwd2 127.0.0.1 6000", "SIGN UP user1 pwd2 127.0.0.1 5000", "SEND DUMMY user1 user2",
    # "CREATE group1 user1 100", "CREATE group2 user2 200", "JOIN group1 user2", "JOIN group2 user1", "LIST groups user1"]
    # for message in messages:
    #     message = '@'.join(message.split(' '))
    #     try:
    #         result = parse_message(data, message)
    #         print(result)
    #     except Exception as e:
    #         print(e)
    #         break