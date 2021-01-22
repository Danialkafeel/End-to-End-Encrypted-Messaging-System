import os, sqlite3, json
import re

database_path = "./MyDatabase.db"
json_file_path = "./queries.json"
delimiter = '@'

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

def parse_message(data, message):
    username = message.split(delimiter)[2]
    
    if IfExists('SIGN' + delimiter + 'UP', message):
        if IsAccountExist(username):
            return '0' + delimiter + 'Username already exists'
        else:
            password = 'pwd1'
            ip = '127.0.0.1'
            port = '5000'
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

            return '1' + "You are signed in"

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
            try:
                #Pay attention here
                randomkey = message.split(delimiter)[3]
            
            except Exception as e:
                randomkey = '300'

            members = username
            query_to_execute = data['queries']['insert_into'].format("Group_info", add_quotes(group) + ',' + add_quotes(members) + ',' + add_quotes(randomkey))
            execute_query(query_to_execute)

            #get number of people in group
            number_of_people_in_group = 1

            return '1' + delimiter + "Group created" + delimiter + str(number_of_people_in_group)

        #Should I send random key also here?
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

            ####Update group members####
            ##Get members already in group
            query_to_execute = data['queries']['get_column_conditional_query'].format('members', 'Group_info', 'Groupname = {}'.format(add_quotes(group)))
            group_members = execute_query(query_to_execute)
            group_members = group_members[0][0]
            number_of_people_in_group = len(group_members.split(delimiter))+1
            
            group_members = group_members + delimiter + username
            query_to_execute = data['queries']['update_query'].format("Group_info", "members = {}".format(add_quotes(group_members)), "Groupname = {}".format(add_quotes(group)))
            execute_query(query_to_execute)
            
            return '1' + delimiter + 'You have joined the group' + delimiter + str(number_of_people_in_group)

        return '0' + delimiter + 'Request is not appropriate'

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


if __name__ == "__main__":
    data = init_db()

    messages = ["SIGN UP user1 pwd1 127.0.0.1 5000", "SIGN UP user2 pwd2 127.0.0.1 6000", "SIGN UP user1 pwd2 127.0.0.1 5000", "SEND DUMMY user1 user2",
    "CREATE group1 user1 100", "CREATE group2 user2 200", "JOIN group1 user2", "JOIN group2 user1", "LIST groups user1"]
    for message in messages:
        message = '@'.join(message.split(' '))
        try:
            result = parse_message(data, message)
            print(result)
        except Exception as e:
            print(e)
            break