# END TO END MESSAGING SYSTEM   

## FLOW AND WORKING
* A automated program is executed to start desired number of *Servers* for the application.
* *Loadbalancer* program is started on specified Port number, which uniformly distributes the requests from the different different clients to different Servers accordingly.
* Various *Clients* program are started on different Port nos and all clients are binded to the *Loadbalancer*.
* *Clients* can directly send to messages or any file to other clients. Clients can created or join various groups and then send messages or files to different different groups.
* All the messages and files are encrypted using Triple DES (3DES) encyrption algorithm. Keys between clients are shared using Diffie–Hellman key key exchange algorithm 

## Various Commands for Client
* *Sign up <username> <rollnumber> <password>* - For signing up clients for first time.
* *Login <usernamer+rollnumber> <password>* - For logging into their account.
* *Send <Name+Rollno.> <message>*          - Sending message to any specific client.            
* *Send_file file_name <Name||Rollno.>*    -Sending File to any specific client.
* *Send_group <No.ofgroups> <Groupno.(s)> <message>* - Sending group message.
* *Send_group_File <File_Name>  <No.ofgroups> <Groupno.(s)>* Sending group file.
* *Create <Groupname>* -Creating a new Group.
* *Join <Groupname>*   - Joining Specific Group.
* *Show_my_groups*    - Displaying groups where I am a member
* *List*             - Listing avaliable groups to join.

## Snapshots of the Application with various Commands
    * Sign Up
            ![alt text](https://github.com/Danialkafeel/End-to-end-messaging-system/blob/main/Images/2_signup_menu.png)

    -> *Login <usernamer+rollnumber> <password>* 

            [[Screesnhot]]

    -> *Create <Groupname> 

            [[Screesnhot]]

    -> *Join <Groupname>   

            [[Screesnhot]]

    -> *Show_my_groups*   

            [[Screesnhot]]

    -> *List*             

            [[Screesnhot]]

    -> *Send <Name+Rollno.> <message>*          

            [[Screesnhot]]


    -> *Send_file file_name <Name||Rollno.>*   

            [[Screesnhot]]

    -> *Send_group <No.ofgroups> <Groupno.(s)> <message>* 

            [[Screesnhot]]

    -> *Send_group_File <File_Name>  <No.ofgroups> <Groupno.(s)>* 

            [[Screesnhot]]
