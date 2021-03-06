// CMSC 23300
// Project 1
// Max Liu
// CNET: maxliu
// Fall 2018
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>


void parseCommandArgs(int argc, char *argv[], int *flags);
void errorInput();
void errorOther();
void error(char *msg);
void runServer(int argc, char *argv[], int *flags);
void runClient(int argc, char *argv[], int *flags);


int main(int argc, char *argv[])
{
    int flags[3] = {0, 0, 0};

    // parse the given commands and check if there is an error
    parseCommandArgs(argc, argv, flags);

    // now we need to see if we should run as a client or as a server
    if (flags[0]) {
        // run as server
        // printf("running as server\n");
        runServer(argc, argv, flags);
    } else {
        // run as client
        // printf("running as client\n");
        runClient(argc, argv, flags);
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


// exit with specific error message
void error(char *msg)
{
    fprintf(stderr, "%s", msg);
    exit(1);
}


// server side code
void runServer(int argc, char *argv[], int *flags)
{
    int sockfd, newsockfd, portno, clilen;
    char buffer[256];
    struct sockaddr_in serv_addr, cli_addr;
    socklen_t addrlen = sizeof(cli_addr);
    struct hostent *server;
    int n;

    // first need to know to use either TCP or UDP
    if (flags[1]) {
        // use UDP
        // printf("using UDP\n");
        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    } else {
        // use TCP
        // printf("using TCP\n");
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
    }
    if (sockfd < 0) {
        error("ERROR opening socket\n");
    }

    bzero((char *) &serv_addr, sizeof(serv_addr));
    portno = atoi(argv[argc - 1]);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(portno);
    //see if we need to set a hostname
    if (flags[2]) {
        // set the hostname to the user specified one
        // printf("setting server address to %s\n", argv[argc - 2]);
        server = gethostbyname(argv[argc - 2]);
        if (!server) {
            error("ERROR invalid hostname\n");
        }
        bcopy((char *) server->h_addr, 
              (char *) &serv_addr.sin_addr.s_addr, 
              server->h_length);
    } else {
        // set it to defualt
        // printf("setting server address to INADDR_ANY\n");
        serv_addr.sin_addr.s_addr = INADDR_ANY;
    }

    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        error("ERROR on binding\n");
    }

    if (flags[1]) {
        // used UDP so we dont need to listen() or accept()
        while (1) {
            bzero(buffer, 256);
            n = recvfrom(sockfd, buffer, 255, 0, 
                         (struct sockaddr *) &cli_addr, (socklen_t *) &addrlen);
            if (n < 0) {
                error("ERROR on receive\n");
            }
            printf("%s", buffer);
        }
    } else {
        // used TCP so we need to listen() and accept()
        listen(sockfd, 5);
        clilen = sizeof(cli_addr);
        newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, 
                           (socklen_t *) &clilen);
        if (newsockfd < 0) {
            error("ERROR on accept\n");
        }
        
        while (1) {
            bzero(buffer, 256);
            // n = read(newsockfd, buffer, 255);
            n = recv(newsockfd, buffer, 255, 0);
            if (n < 0) {
                error("ERROR reading from socket\n");
            }
            if (n == 0) {
                // close the connection
                close(newsockfd);
                // error("ERROR connection lost\n");
                exit(0);
            }
            printf("%s", buffer);
        }
    }
}


// client side code
void runClient(int argc, char *argv[], int *flags)
{
    int sockfd, portno, n;
    int wr = 1;

    struct sockaddr_in serv_addr;
    struct hostent *server;

    char buffer[256];

    portno = atoi(argv[argc - 1]);

    // first need to know to use either TCP or UDP
    if (flags[1]) {
        // use UDP
        // printf("using UDP\n");
        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    } else {
        // use TCP
        // printf("using TCP\n");
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
    }
    if (sockfd < 0) {
        error("ERROR opening socket\n");
    }

    // get the server
    server = gethostbyname(argv[argc - 2]);
    if (server == NULL) {
        error("ERROR no such host\n");
    }

    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *) server->h_addr, 
          (char *) &serv_addr.sin_addr.s_addr, 
          server->h_length);
    serv_addr.sin_port = htons(portno);

    if (flags[1]) {
        // used UDP so we do not need to connect()
        while (1) {
            bzero(buffer, 256);
            if (fgets(buffer, 255, stdin) == NULL) {
                // Ctrl-D was pressed and we need to stop sending messages
                // but we do not need to close the application
                shutdown(sockfd, SHUT_WR);
                wr = 0;
            }
            if (wr) {
                n = sendto(sockfd, buffer, strlen(buffer), 0, 
                           (struct sockaddr *) &serv_addr, sizeof(serv_addr));
                if (n < 0) {
                    error("ERROR sending message\n");
                }
            } 
        }

    } else {
        // used TCP so we need to connect()
        if (connect(sockfd, (struct sockaddr *) &serv_addr, 
        sizeof(serv_addr)) < 0) {
        error("ERROR connecting\n");
        }

        while (1) {            
            bzero(buffer, 256);
            if (fgets(buffer, 255, stdin) == NULL) {
                // Ctrl-D was pressed and we need to exit
                close(sockfd);
                exit(0);
            }
            
            n = send(sockfd, buffer, strlen(buffer), 0);
            // n = write(sockfd, buffer, strlen(buffer));
            if (n < 0) {
                error("ERROR writing to socket\n");
            }
        }
    }
}