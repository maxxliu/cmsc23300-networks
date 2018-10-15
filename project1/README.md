Max Liu

CNET: maxliu

## Compile

run: make

## Execute

usage: ./snc [-l] [-u] [hostname] port

-l       : tells application to run as server and listen for connections

-u       : tells application to use UDP instead of TCP

hostname : address used to listen or contact

port	 : port used to listen or contact

NOTE: one of [-l] [-u] [hostname] must be given

## Design

At a high level, a user can call the program using ./snc and provide to it a set
of arguments. These arguments are then parsed to determine their validity and 
appropriate calls to other functions are made, otherwise an error is given. This ensures
that most invalid TCP/UDP calls are not used and provides an intuituve way to see how the
program is running

**If run as server** the program will listen at the specified port and bind to the specific
hostname if it is given as an argument. TCP is used as default. Under TCP, the server will
close if it loses connection to the client. If the UDP specification is given, the server will
listen until the user manually closes it. To be more clear, **Ctrl-D will have no effect if
entered on the server side**, but Ctrl-D can close the server if the client enters it and
both are running TCP

**If run as client** the program will run TCP by default and try to establish a connection with 
a server and will fail if the connection cannot be established. If a connection is established,
entering Ctrl-D will terminate both the client and the server. If UDP is specified, Ctrl-D
will not terminate the client or server, but the client will no longer be able to send messages 

**Note that multithreading has not been implemented** so the server cannot send messages and
the client cannot read messages

## Key Functions

```
void parseCommandArgs(int argc, char *argv[], int *flags)
```

Parses the arguments that the user input. Goes through preliminary checks to ensure 
validity of the arguments. An array is used to keep track of which flags were given
and this array is then passed to the server/client code to guide the functions on
how to set up the server/client 

```
void runServer(int argc, char *argv[], int *flags)
```

Runs program as server and listens for connections and messages. A while loop is used to 
keep the program running until it is manually closed or if it senses that the connection
has been lost. The flags array is used to keep track of the arguments passed by the user.
This provides an organized way to properly set up the server

```
void runClient(int argc, char *argv[], int *flags)
```

Runs the program as a client and tries to connect or send messages to the specified hostname
and port. A while loop is used to keep the program running until a user closes the connection.
Again the flags array is used to keep track of the users arguments to set up the client

## Issues Encountered

Encountered some issues with the separate implementation of TCP and UDP. Initially tried to 
connect sockets even under UDP before realizing that it was not neccessary

Issues with getting program to give an error message when invalid hostname and port are given.
The program was somehow not crashing and still trying to listen on a hostname and port even
when the hostname was not a valid hostname for the program to bind to. This was resolved
by using a different function to check the validity of the given hostnames on both the client
and server side. 
