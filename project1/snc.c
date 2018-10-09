// CMSC 23300
// Project 1
// Max Liu
// CNET: maxliu
// Fall 2018
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>


void parseCommandArgs(int argc, char *argv[], int *flags);


int main(int argc, char *argv[])
{
    

    int flags[3];
    parseCommandArgs(argc, argv, flags);

    // first I want to check the command line arguments to make sure that the 
    // user has input a valid call to the program


    // int i = 0;
    // char c[100];
    // c = argv[i];
    // printf("%s\n", argv[1]);
    // printf("argc = %i\n", argc);
    // while (1) {

    // }

    return 0;
}


// return an integer array with a 1 or 0 specifying if a certain flag is present
// or not, could also possible be an invalid call to the program
// structure will be:
// [-l flag, -u flag, hostname]
void parseCommandArgs(int argc, char *argv[], int *flags)
{



}

