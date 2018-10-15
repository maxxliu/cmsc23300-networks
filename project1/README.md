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
appropriate calls to other functions are made, otherwise an error is given.

**If run as server** the program will listen at the specified port and bind to the specific
hostname if it is given as an argument. TCP is used as default. Under TCP, the server will
close if it loses connection to the client. If the UDP specification is given, the server will
listen until the user manually closes it. To be more clear, **Ctrl-D will have no effect if
entered on the server side**, but Ctrl-D can close the server if the client enters it and
both are running TCP.

**If run as client** the program will run TCP by default and try to establish a connection with 
a server and will fail if the connection cannot be established. If a connection is established,
entering Ctrl-D will terminate both the client and the server. If UDP is specified, Ctrl-D
will not terminate the client or server, but the client will no longer be able to send messages. 

**Note that multithreading has not been implemented** so the server cannot send messages and
the client cannot read messages.

## Key Functions

```
void parseCommandArgs(int argc, char *argv[], int *flags)
```

```
void runServer(int argc, char *argv[], int *flags)
```

```
void runClient(int argc, char *argv[], int *flags)
```

## Issues Encountered

overview of issues encountered
