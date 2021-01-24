import sqlite3

tables = ['User', 'Group_info']
database_path = "./MyDatabase.db"

for table in tables:
    query = "SELECT * FROM {}".format(table)

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
    #connection.commit() 

    print(table)
    print(query_result)
    print('\n')
    
    # close the connection 
    connection.close()