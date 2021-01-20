import os, sqlite3, json
import re

database_path = "./MyDatabase.db"
json_file_path = "./queries.json"
data = None
delimiter = '*'

def IfExists(string1, string2):
    pass

def IsAccountExist(username):
    query_to_execute = data['queries']['get_column'].format("Username", "User")
    usernames = execute_query(query_to_execute)
    
    return IfExists(username, usernames)

def IsPasswordExist(password):
    query_to_execute = data['queries']['get_column'].format("password", "User")
    passwords = execute_query(query_to_execute)
    
    return IfExists(password, passwords)

def IsSignedIn(username):
    query_to_execute = data['queries']['get_column_conditional_query'].format("IsSignedIn", "User", "Username = {}".format(username))
    status = execute_query(query_to_execute)
    
    return status == '1'

def execute_query(query):
    # connecting to the database 
    connection = sqlite3.connect(database_path)
    
    #cursor
    crsr = connection.cursor()
    
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

def parse_messgae(message):
    if IfExists("SIGN UP", message):
        if IsAccountexist(username):
            return '0' + delimiter + 'Username already exists'
        else:
            password = ''
            ip = ''
            port = ''
            query_to_execute = data['queries']['insert_into'].format("User", username, password, ip, port, '1', '')
            execute_query(query_to_execute)

            ###Update query, change the signed in column status
            query_to_execute = data['queries']['update_query'].format("User", "IsSignedIn = '1'", "Username = {}".format(username))
            execute_query(query_to_execute)

            return '1' + delimiter + 'Your account has been made'
    else:
        if IfExists("SIGN IN", message):
            if IsAccountexist(username):
                return '0' + delimiter + 'Username is incorrect'
            
            if IsPasswordExist(password):
                return '0' + delimiter + 'Password is incorrect'
    
            ###Update query, change the signed in column status
            query_to_execute = data['queries']['update_query'].format("User", "IsSignedIn = '1'", "Username = {}".format(username))
            execute_query(query_to_execute)

            return '1' + "You are signed in"

        elif ifExists("SEND", message):
            peer_name = ''
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedin(username):
                return '0' + delimiter + 'You are not Signed in'

            if not IsAccountExist(peer_name):
                return '0' + delimiter + 'Peer which you are sending message to doesnt exist'
            
            query_to_execute = data['queries']['get_column_conditional_query'].format("ip", "User", "Username = {}".format(username))
            ip = execute_query(query_to_execute)

            query_to_execute = data['queries']['get_column_conditional_query'].format("port", "User", "Username = {}".format(username))
            port = execute_query(query_to_execute)

            return '1' + ip + delimiter + port
        
        elif ifExists("LIST", message):
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedin(username):
                return '0' + delimiter + 'You are not Signed in'

            if not IsAccountExist(peer_name):
                return '0' + delimiter + 'Peer which you are sending message to doesnt exist'

            query_to_execute = data['queries']['get_column'].format("Groupname", "Group_info")
            groups = execute_query(query_to_execute)

            return 1 + delimiter + groups
        
        elif ifExists("CREATE", message):
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedin(username):
                return '0' + delimiter + 'You are not Signed in'

            if not IsAccountExist(peer_name):
                return '0' + delimiter + 'Peer which you are sending message to doesnt exist'
            
            if IsGroupExist(group):
                return '0' + delimiter + 'A group with this name already exists'
            
            randomkey = ''
            members = username
            query_to_execute = data['queries']['insert_into'].format("Group_info",members, randomkey)

            #get number of people in group
            number_of_people_in_group = 1

            return '1' + delimiter + "Group created" + delimiter + str(number_of_people_in_group)

        
        elif ifExists("JOIN", message):
            if not IsAccountExist(username):
                return '0' + delimiter + 'Make an account first'
            
            if not IsSignedin(username):
                return '0' + delimiter + 'You are not Signed in'

            if not IsAccountExist(peer_name):
                return '0' + delimiter + 'Peer which you are sending message to doesnt exist'
            
            if not IsGroupExist(group):
                randomkey = ''
                members = username
                query_to_execute = data['queries']['insert_into'].format("Group_info",members, randomkey)
                
                #get number of people in group
                number_of_people_in_group = 1

                return '1' + delimiter + "Group created" + delimiter + str(number_of_people_in_group)
            
            ##Get members already in group
            query_to_execute = data['queries']['get_column_conditional_query'].format('members', 'Group_info', 'Groupname = {}'.format(group))
            group_members = execute_query(query_to_execute)
            number_of_people_in_group = len(group_members.split(delimiter))+1
            
            ####Update group members####
            group_members = group_members + delimiter + username
            query_to_execute = data['queries']['update_query'].format("Group_info", "members = {}".format(group_members), "Groupname = {}".format(group))
            execute_query(query_to_execute)
            
            return '1' + delimiter + 'You have joined the group' + delimiter + str(number_of_people_in_group)

        return '0' + delimiter + 'Request is not appropriate'

def init_db():
    #print("hey")
    if not os.path.isfile(database_path):
        with open(json_file_path) as f:
            data = json.load(f)
            for table_name in data['tables'].keys():
                query_to_execute = data["queries"]["create_table"]
                schema = " VARCHAR (20) ,".join(data["tables"][table_name]["schema"])
                query_to_execute = query_to_execute.format(table_name, schema)
                print(query_to_execute)
                execute_query(query_to_execute)


    else:
        print("Database File already exists")


if __name__ == "__main__":
    init_db()

    message = "SIGN UP user1 passwd"
    print(parse_messgae(message))