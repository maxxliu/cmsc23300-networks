// CMSC 23300
// Project 1
// Max Liu
// CNET: maxliu
// Fall 2018
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>


void parseCommandArgs(int argc, char *argv[], int *flags);
void errorInput();


int main(int argc, char *argv[])
{
    

    int flags[3] = {0, 0, 0};
    parseCommandArgs(argc, argv, flags);

    // first I want to check the command line arguments to make sure that the 
    // user has input a valid call to the program


    // int i = 0;
    // char c[100];
    // c = argv[i];
    // printf("%s\n", argv[1]);
    // printf("argc = %i\n", argc);
    while (1) {

    }

    return 0;
}


// return an integer array with a 1 or 0 specifying if a certain flag is present
// or not, could also possible be an invalid call to the program
// structure will be:
// [-l flag, -u flag, hostname]
void parseCommandArgs(int argc, char *argv[], int *flags)
{
    int port;
    int ignore = 1;
    int i;
    char c;

    // first check to see if there are enough arguments
    // there should always be at least 2 and no more than 4
    if ((argc < 3) || (argc > 5)) {
        errorInput();
    }

    // the last argument should be the port number
    // port number should be between 1025 and 65535
    port = atoi(argv[argc - 1]);
    if ((port < 1025) || (port > 65535)) {
        errorInput();
    }

    // check to see if the second to last argument is a hostname
    c = argv[argc - 2][0];
    if (c != '-') {
        flags[2] = 1;
    }

    // now we need to iterate through the other possible arguments
    // we already looked at the last 2 arguments so we need to look
    // at the arguments before those
    if (flags[2]) {
        ignore = 2;
    }
    for (i = 1; i < argc - ignore ; i++) {
        if (!strcmp(argv[i], "-l")) {
            flags[0] = 1;
        } else if (!strcmp(argv[i], "-u")) {
            flags[1] = 1;
        } else {
            errorInput();
        }
    }

    // if -l not specified, hostname must be specified
    if ((flags[0] == 0) && (flags[2] == 0)) {
        errorInput();
    }
}


// call when user inputs invalid options
void errorInput()
{
    fprintf(stderr, "invalid or missing options\n"
                    "usage: snc [-l] [-u] [hostname] port\n");
    exit(1);
}


// any other error
void errorOther()
{
    fprintf(stderr, "internal error\n");
    exit(1);
}
