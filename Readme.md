# END TO END MESSAGING SYSTEM   

## Prerequisites and Installation
* Threading `pip3 install threading`
* Socket `pip3 install socket`
* Os `pip3 install os`
* Sys `pip3 install sys`
* Hashlib `pip3 install hashlib`
* Crypto `pip3 install Crypto`
* Time `pip3 install time`
* Base64 `pip3 install bas64`
* Sqlite3 `pip3 install sqlite3`
* JSON `pip3 install json`
* Random `pip3 install random`
* Subprocess `pip3 install subprocess`

## FLOW AND WORKING
* A automated program is executed to start desired number of *Servers* for the application.
`python3 automate_program.py <Number of servers>`
* *Loadbalancer* program is started on specified Port number, which uniformly distributes the requests from the different different clients to different Servers accordingly.
`python3 loadbalancer.py <LoadBalancerPort>`
* Various *Clients* program are started on different Port nos and all clients are binded to the *Loadbalancer*.
`python3 client.py <clientPort> <LoadBalancerPort>`
* *Clients* can directly send to messages or any file to other clients. Clients can created or join various groups and then send messages or files to different different groups.
* All the messages and files are encrypted using Triple DES (3DES) encyrption algorithm. Keys between clients are shared using Diffie–Hellman key key exchange algorithm 

## Various Commands for Client
* `Sign up <username> <rollnumber> <password>` - For signing up clients for first time.
* `Login <usernamer+rollnumber> <password>` - For logging into their account.
* `Send <Name+Rollno.> <message>`          - Sending message to any specific client.            
* `Send_file file_name <Name||Rollno.>`    -Sending File to any specific client.
* `Send_group <No.ofgroups> <Groupno.(s)> <message>` - Sending group message.
* `Send_group_File <File_Name>  <No.ofgroups> <Groupno.(s)>` Sending group file.
* `Create <Groupname>` -Creating a new Group.
* `Join <Groupname>`   - Joining Specific Group.
* `Show_my_groups`    - Displaying groups where I am a member
* `List`             - Listing avaliable groups to join.

##  Interaction Model
![Interaction model](https://github.com/Danialkafeel/End-to-End-Encrypted-Messaging-System/blob/main/Images/snsdiagram.png)

## Class Diagram

![class diagram](https://github.com/Danialkafeel/End-to-end-messaging-system/blob/main/Images/Class%20Diagram.jpg)

## Snapshots of the Application with various Commands

* Automate program to create multiple servers

![alt text](https://github.com/Danialkafeel/End-to-end-messaging-system/blob/main/Images/1_automate_program_for_servers.png)

* Sign Up

![alt text](https://github.com/Danialkafeel/End-to-end-messaging-system/blob/main/Images/2_signup_menu.png)

* Login Menu , List , Create, Join Commands

![alt text](https://github.com/Danialkafeel/End-to-end-messaging-system/blob/main/Images/3_login_menu_and_commands.png)

* Messages between Client to Client and Client to Groups.

![alt text](https://github.com/Danialkafeel/End-to-end-messaging-system/blob/main/Images/4_msg_p2p_and_p2group.png)
