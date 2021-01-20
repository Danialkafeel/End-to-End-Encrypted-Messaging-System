import sys

if "__name__ == __main__":
    try:
        print("Hey")
        #Put the code to create servers here, when server gets created write his info in 		json file
    except Exception as e:
        print(e)
    finally:
 	#Don't remove this, this will keep the terminal from closing when something goes wrong, so that we can see the error message
        input()
    
