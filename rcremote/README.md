rcremote and rcremoteserver
===============================

[![Join the chat at https://gitter.im/robocomp/robocomp](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/robocomp/robocomp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

#How these two components work?

To understand how these components work, we need to have very clear the client-server structure. For example, suppose we have a robot (with his own computer) and our computer, and the robot acts as a server and our computer as a client that needs to access to the robot's services (applications). In this case, the server program (rcremoteserver) will be runned into the robot and the client program (rcremote) will be executed into our computer.
The behaviour of both programs is very similar: both use a default port (4242), an IP address and a password, and work with TCP protocol...

1) rcremoteserver: the server uses its localhost as IP and takes the password that is passed as an input parameter to allow clients to connect or not --> Usage: `rcremoteserver password`

2) rcremote: the client uses the server IP and the server password to connect with him --> Usage example: `rcremote IP_address mytabname /home/robocomp touch argument1 argument2`

###File .rcremote

What happends if we forget to put the password when we run the rcremoteserver or the rcremote program? An error like this will be released:
    
    IOError: [Errno 2] No existe el archivo o el directorio: '/home/<your-linux-user>/.rcremote'

In order to prevet this and facilitate the use of these two programs we can use the file `.rcremote`. This file allows us to use the rcremoteserver and rcremote programs without pass arguments. We just have to create the `.rcremote` file in the HOME directory and follow the format `hostname#password`, for example:

    robot1#passwordrobot1
    robot2#passwordrobot2
    computer1#passwordcomputer1
    computer2#passwordcomputer2
    [...]
    
This way you only need to run "rcremote" on the client and "rcremoteserver" on the server.

###Example: Running rcremote and rcremoteserver to communicate between two terminals on the same PC

1) Run the command $ rcremoteserver abcd123 in one terminal.

2) Create a file named .rcremote in the HOME folder, as indicated above. Add the following line to it:
localhost#abcd123

3) Open the yakuake drop down terminal (Press F12). Install it if you dont have yakuake.

4) In the yakuake terminal, type $ rcremote localhost any_name_here /home/robocomp any_name_here space_separated_arguments

5) On pressing enter, you will see the values entered in the yakuake tab transfered to the terminal window.  


    
    
    



