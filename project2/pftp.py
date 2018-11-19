import threading
import argparse
import socket
import sys
import os
import re


###################
# Argument parser #
###################


parser = argparse.ArgumentParser(description="Passive parallel FTP client")

parser.add_argument('-v', '--version', action='version',
                                       version='%(prog)s 0.1 maxliu')
parser.add_argument('-f', '--file', help='Specifies the file to download',
                                    dest='file')
parser.add_argument('-s', '--server', help='Specifies the server to download \
                                            the file from',
                                      dest='server')
parser.add_argument('-p', '--port', help='Specifies the port to be used when \
                                          contacting the server (default \
                                          value: 21)',
                                    default=21,
                                    type=int,
                                    dest='port')
parser.add_argument('-t', '--thread', help='Each line in the config-file \
                                            specifies the login, password, \
                                            hostname and absolute path to the \
                                            file',
                                      metavar='config-file',
                                      dest='config')
parser.add_argument('-n', '--username', help='Uses the username user when \
                                              logging into the FTP server \
                                              (default value: anonymous)',
                                        default='anonymous',
                                        dest='username')
parser.add_argument('-P', '--password', help='Uses the password password when \
                                              logging into the FTP server \
                                              (default value: \
                                              user@localhost.localnet)',
                                        default='user@localhost.localnet',
                                        dest='password')
parser.add_argument('-l', '--log', help='Logs all the FTP commands exchanged \
                                         with the server and the corresponding \
                                         replies to file logfile. If the \
                                         filename is "-" then the commands are \
                                         printed to the standard output',
                                    dest='log')

def check_args(args):
    '''
    check if the given arguments are valid, for example, if server and file are
    not given, then a thread file must be given
    this is run before doing anything related to sockets and ftp. we just want
    to check at a high level that the given arguments make sense
    checks:
        thread file argument is valid if given
        file and server given, or thread config file given

    inputs:
        args (argparse object) - holds the values of the command line args

    outputs:
        run_as (str) - single or parallel
        OR
        None, will print an error message to stderr and then exit with exit
        code 7 (generic error) OR will print argparse help
    '''
    # check that either
    # 1) server and file are given
    # 2) thread file is given
    # if both are given then show the help page
    if args.server and args.file and args.config:
        print('HINT: cannot specify thread if server and file are given')
        error_07()
    elif args.server and args.file:
        # check that protocal is correct if it is given
        tmp = args.server.split('//')
        if len(tmp) > 1:
            if tmp[0] != 'ftp:':
                # no other protocols are allowed
                print('HINT: need to use ftp:// if you specify a protocol')
                error_04()
        return 'single'
    elif args.config:
        # check that the given config file is valid
        if not os.path.isfile(args.config):
            print('HINT: config file specified does not exist')
            error_07()
        return 'parallel'
    else:
        print('HINT: need to specify both server and file')
        error_07()


##################
# Error messages #
##################


def error_00():
    print('Operation successfully completed')
    sys.exit(0)
def error_01():
    print('ERROR: Cannot connect to server', file=sys.stderr)
    sys.exit(1)
def error_02():
    print('ERROR: Authentcation failed', file=sys.stderr)
    sys.exit(2)
def error_03():
    print('ERROR: File not found', file=sys.stderr)
    sys.exit(3)
def error_04():
    print('ERROR: Syntax error in client request', file=sys.stderr)
    sys.exit(4)
def error_05():
    print('ERROR: Command not implemented by server', file=sys.stderr)
    sys.exit(5)
def error_06():
    print('ERROR: Operation not allowed by server', file=sys.stderr)
    sys.exit(6)
def error_07():
    print('ERROR: Generic error', file=sys.stderr)
    sys.exit(7)


###########
# Sockets #
###########


def recv_msg(sock, lf, name=None):
    '''
    receive the message, print or write to file if needed, and check to see if
    there were any errors

    intputs:
        sock (socket) - connection to the ftp server
        lf (open file) - file to write to, if it is '-' then print to screen
        name (int) - thread number

    outputs:
        data (str) - the response received from the ftp server
        OR
        None, if there is an error, print to stderr and then exit with the
        appropriate exit code
    '''
    # change name really quickly
    if name:
        name = 'Thread ' + str(name) + ': '
    else:
        name = ''
    buff = 1 # now we can only read one line at a time
    # recv the message
    try:
        data = sock.recv(buff)
    except:
        print("ERROR: Could not receive bytes from server")
        error_07()
    # check that we are at the end
    while data.decode()[-1] != '\n':
        try:
            to_add = sock.recv(buff)
        except:
            print("ERROR: Could not receive bytes from server")
            error_07()
        data += to_add
    # decode the data and strip returns
    # NOTE: this is no longer neccessary (to split) but regardless should not
    #       make a difference when running
    data = data.decode()
    data = data.split('\r\n')
    for d in data:
        # if its an empty string just move on to the next one
        if len(d) == 0:
            break
        # handle the log file
        if lf:
            line = name + 'S->C: ' + d
            if lf =='-':
                # print to screen
                print(line)
            else:
                # write to the file
                lf.write(line + '\n')
        # check for errors
        check_ftp_code(int(d[:3]), sock)

    return data


def send_msg(sock, lf, msg, name=None):
    '''
    send a message, write/print to log file if specified

    imports:
        sock (socket) - connection to ftp server
        lf (open file) - file to write to, if it is '-' then print to screen
        msg (str) - message to send, will be encoded to bytes before sending
                    we are assuming that the msg does not already have the
                    \r\n appended to the end yet
        name (int) - thread number

    outputs:
        None, if there is an errorm print to stderr and then exit with the
        appropriate exit code
    '''
    # change name really quickly
    if name:
        name = 'Thread ' + str(name) + ': '
    else:
        name = ''
    # strip away the '\r\n' if it is there
    msg = msg.strip('\r\n')
    # handle the log file
    if lf:
        line = name + 'C->S: ' + msg
        if lf == '-':
            # print to screen
            print(line)
        else:
            # write to the file
            lf.write(line + '\n')
    # add return and encode to bytes
    msg += '\r\n'
    msg = msg.encode()
    # try to send the message
    try:
        sock.sendall(msg)
    except:
        print('ERROR: Could not send message to server')
        error_07()


def check_ftp_code(code, sock):
    '''
    given an ftp response code, determine what action to take. code can
    either be ok or not be ok in which we display appropriate error message
    NOTE: I do not check for 426, this is because 426 will happen in
          multi-thread when connections are closed halfway through. The
          program will also check that the returned value is the correct size
          afterwards so this is fine

    inputs:
        code (int) - response code given by the ftp server
        sock (socket connection) - this needs to be closed in case of error

    outputs:
        None, if there is an error, print to stderr and then exit with the
        appropriate exit code
    '''
    if code == 530:
        sock.shutdown(socket.SHUT_RDWR);sock.close()
        error_02()
    if code in {500, 502}:
        sock.shutdown(socket.SHUT_RDWR);sock.close()
        error_05()
    if code == 425:
        sock.shutdown(socket.SHUT_RDWR);sock.close()
        error_04()
    if code in {550, 553}:
        sock.shutdown(socket.SHUT_RDWR);sock.close()
        error_06()


def pasv_port(data):
    '''
    takes the message sent by ftp server after the PASV command and returns the
    port that the client should connect to

    inputs:
        data (str) - response from ftp server after PASV command

    outputs:
        port (int) - port to recv data from
    '''
    data = data.strip(').').split(',')
    port = (int(data[-2]) * 256) + int(data[-1])

    return port


def recv_file(server, port, total, main_sock, lf, position=None):
    '''
    after the ftp server gives a port to receive data from, open a connection
    to the server and that port and receive the data, only receive amount of
    bytes specified by total

    inputs:
        server (str) - server name to connect to
        port (int) - port number to connect to
        total (int) - stop reading after receiving this many bytes, if it is
                      not parallel then this number should just be the size of
                      the full file
         main_sock (socket connection) - connection from the main function
         lf (log file)
         position (int)

    outputs:
        data (byte str) - the bytes that were returned by server
        OR
        exits with appropriate exit code becuase cannot retrieve file
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_address = (server, port)
    try:
        sock.connect(serv_address)
    except:
        # error connecting
        error_01()
    # check that the other side is ok
    recv_msg(main_sock, lf, position)

    # now we need to receive the file
    buff = int(total / 4)
    try:
        data = sock.recv(buff)
    except:
        print("ERROR: Could not receive bytes from server")
        error_07()
    while len(data) < total:
        try:
            to_add = sock.recv(buff)
        except:
            print("ERROR: Could not receive bytes from server")
            error_07()
        # add to the data we have received so far
        data += to_add

    return data


def recv_list(server, port, main_sock, lf, position=None):
    '''
    NOTE: this was only used to find the byte sizes of the files (I did not
          realize there was a SIZE command) however this works and I will
          keep using it for now

    return back the data that is sent by the server after LIST command, this
    functions is separate from the recv file because I am not sure how to find
    the expected length of the directiry informations sent back by the server

    inputs:
        server (str) - server name to connect to
        port (int) - port number to connect to
        main_sock (main socket connections) - from the func that called this
        lf (log file)
        position (int)

    ouputs:
        data (str) - data sent by the server
        OR
        exits with appropriate exit code because cannot connect or recv
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_address = (server, port)
    try:
        sock.connect(serv_address)
    except:
        # error connecting
        error_01()
    # first check to see that everything is ok on the other side
    recv_msg(main_sock, lf, position)

    # now we need to receive the list of files
    buff = 16384 # recv large amount so hopefully we get everything
    try:
        data = sock.recv(buff)
    except:
        print("ERROR: Could not receive bytes from server")
        error_07()
    # this is not perfect but I know that the last character must be the
    # newline character
    while data.decode()[-1] != '\n':
        try:
            to_add = sock.recv(buff)
        except:
            print("ERROR: Could not receive bytes from server")
            error_07()
        # add to the data we have received so far
        data += to_add

    return data.decode()


def get_file_size(data, file):
    '''
    NOTE: I have recently discovered that this can be accomplished using SIZE
          however I will continue to use this function for now...

    given the data sent for LIST we parse the returned value and return the
    expected byte length for a file

    inputs:
        data (str) - data that was returned by LIST
        file (str) - the file that the user is looking for

    outputs:
        size (int) - size of the file
    '''
    # use regex to find the size of files
    p = '([0-9]+) [a-zA-Z]+ [0-9]+ [0-9]+:[0-9]+ ([a-zA-Z0-9.-_]+)\r\n'
    matches = re.findall(p, data)
    # go through the matches and look for the specified file
    for m in matches:
        if file == m[1]:
            size = int(m[0])
            return size
    # if no matches found then give an error
    error_03()


###################################
# Retrieving data from ftp server #
###################################


def single_ftp(args):
    '''
    takes the command line arguments and uses a single thread to extract the
    specified files. if the program gets to this stage then we can assume that
    the given argument types are valid and there are no obvious things wrong
    with the arguments (server, user, password, etc. could still all be wrong)

    inputs:
        args (argparse object) - holds all of the user arguments

    outputs:
        None, will exit with 0 for success or will exit with an error message
        and the appropriate error code
    '''
    # lets check if we need to open a new file to write to
    if args.log:
        if args.log == '-':
            lf = '-'
        else:
            # open the file
            lf = open(args.log, 'w')
    else:
        lf = None

    # first we need to set up the socket conenction
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_address = (args.server, args.port)
    try:
        sock.connect(serv_address)
        recv_msg(sock, lf)
    except:
        error_01()

    # log into the server now
    send_msg(sock, lf, 'USER ' + args.username)
    recv_msg(sock, lf)
    send_msg(sock, lf, 'PASS ' + args.password)
    recv_msg(sock, lf)

    # look for the file in the server and find its size
    send_msg(sock, lf, 'PASV')
    pasv = recv_msg(sock, lf)
    port = pasv_port(pasv[0])
    send_msg(sock, lf, 'TYPE I')
    recv_msg(sock, lf)
    send_msg(sock, lf, 'LIST')
    f_list = recv_list(args.server, port, sock, lf) # list of files
    recv_msg(sock, lf) # ftp server daying that data was sent ok
    size = get_file_size(f_list, args.file)

    # retrieve the file
    send_msg(sock, lf, 'PASV')
    pasv = recv_msg(sock, lf)
    port = pasv_port(pasv[0])
    send_msg(sock, lf, 'TYPE I')
    recv_msg(sock, lf)
    send_msg(sock, lf, 'RETR ' + args.file)
    file = recv_file(args.server, port, size, sock, lf)
    recv_msg(sock, lf) # ftp server saying that data was sent ok
    # check that we have the expected number of bytes
    if len(file) != size:
        print('ERROR: Did not retireve all bytes from file')
        error_07()
    f = open(args.file, 'wb')
    f.write(file)
    f.close()

    # close the connection
    send_msg(sock, lf, 'QUIT')
    recv_msg(sock, lf)
    sock.close()

    # close the log file if needed
    if lf and (lf != '-'):
        lf.close()

    error_00()


def parallel_ftp(args):
    '''
    takes the given arguments and retrieves the file using parallel threads

    inputs:
        args (argparse object) - holds all of the user argument

    outputs:
        None, will exit with 0 for success or will exit with an error message
        and the appropriate error code
    '''
    thread_args = process_config(args)
    num = len(thread_args)
    # process log
    if args.log:
        if args.log == '-':
            lf = '-'
        else:
            # open the file
            lf = open(args.log, 'w')
    else:
        lf = None

    # threading
    ret_data = [b'' for t in thread_args] # hold returned data for each thread
    threads = [] # holds the threads
    for i, arg in enumerate(thread_args):
        i += 1
        t = threading.Thread(target=thread_ftp,
                             args=(arg, lf, i, num, ret_data))
        threads.append(t)
    # start the threads
    for t in threads:
        t.start()
    # get the threads back
    for t in threads:
        t.join()

    # ret data needs to be put together to make the file
    final_file = b''
    for f in ret_data:
        if len(f) == 0:
            # something went wrong, throw error
            print('ERROR: Failed to retrieve all parts of the file')
            error_07()
        final_file += f
    f = open(thread_args[0]['file'], 'wb')
    f.write(final_file)
    f.close()

    error_00()


def thread_ftp(args, lf, position, total, ret_data):
    '''
    opens a connection and extracts a certain number of bytes from the
    specified file from a certain position based on the thread number

    inputs:
        args (dict) - holds data on server, file, user, pass, port
        lf (file or None) - log file
        position (int) - thread number
        total (int) - total number of threads
        ret_data (list) - use this to hold the retrieved data

    outputs:
        None, will exit with 0 if everything runs as expected
    '''
    # first we need to set up the socket conenction
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_address = (args['server'], args['port'])
    try:
        sock.connect(serv_address)
        recv_msg(sock, lf, position)
    except:
        error_01()

    # log into the server now
    send_msg(sock, lf, 'USER ' + args['username'], position)
    recv_msg(sock, lf, position)
    send_msg(sock, lf, 'PASS ' + args['password'], position)
    recv_msg(sock, lf, position)

    # look for the file in the server and find its size
    send_msg(sock, lf, 'PASV', position)
    pasv = recv_msg(sock, lf, position)
    port = pasv_port(pasv[0])
    send_msg(sock, lf, 'TYPE I', position)
    recv_msg(sock, lf, position)
    send_msg(sock, lf, 'LIST', position)
    f_list = recv_list(args['server'], port, sock, lf, position) # list of files
    recv_msg(sock, lf, position) # ftp server daying that data was sent ok
    size = get_file_size(f_list, args['file'])

    # we need to figure out what block of bytes this thread should get
    start = (position - 1) * int(size / total)
    block = int(size / total)
    if position == total:
        # this is the final block, just get everything
        block = size - start

    # retrieve the file
    send_msg(sock, lf, 'PASV', position)
    pasv = recv_msg(sock, lf, position)
    port = pasv_port(pasv[0])
    send_msg(sock, lf, 'TYPE I', position)
    recv_msg(sock, lf, position)
    # restart position
    send_msg(sock, lf, 'REST ' + str(start), position)
    recv_msg(sock, lf, position)
    send_msg(sock, lf, 'RETR ' + args['file'], position)
    file = recv_file(args['server'], port, block, sock, lf, position)
    recv_msg(sock, lf, position) # ftp server daying that data was sent ok

    # put the retrieved data in the correct place
    ret_data[position - 1] = file

    # close the connection
    send_msg(sock, lf, 'QUIT', position)
    recv_msg(sock, lf, position)
    sock.close()

    error_00()


def process_config(args):
    '''
    process the config file that was given by the user

    inputs:
        args (argparse object) - contains all the user arguments

    outputs:
        thread_args (list) - a list of dicts with each one containing
                             information on server, file, user, pass
    '''
    # open and read the file
    try:
        f = open(args.config)
    except:
        error_03()
    f = f.read()
    f = f.split('\n')
    f = [i for i in f if len(i) > 0] # remove empty strings
    expect = len(f) # expect this number of threads
    f = [i for i in f if i[:6] == 'ftp://'] # must specify ftp protocol
    if len(f) != expect:
        print('ERROR: Config file not formatted correctly')
        error_04()
    # now need to get the info out of each line
    thread_args = []
    p = 'ftp://([a-zA-Z0-9_.-]+):([a-zA-Z0-9_.-]+)' + \
        '@([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)'
    for i in f:
        # expect to extract 4 data points from each line
        data = re.findall(p, i)
        if len(data) == 1:
            data = data[0]
        else:
            print('ERROR: Config file not formatted correctly')
            error_04()
        if len(data) != 4:
            print('ERROR: Config file not formatted correctly')
            error_04()
        d = {}
        d['username'] = data[0]
        d['password'] = data[1]
        d['server'] = data[2]
        d['file'] = data[3]
        d['port'] = args.port
        thread_args.append(d)
    # check that file names are all the same
    n = [i['file'] for i in thread_args]
    n = set(n)
    if len(n) > 1:
        print('ERROR: Config file not formatted correctly')
        error_04()

    return thread_args


if __name__ == '__main__':
    # parse command line arguments and check if valid
    args = parser.parse_args()
    run_as = check_args(args)

    if run_as == 'single':
        # run as single threaded ftp
        single_ftp(args)
    elif run_as == 'parallel':
        # run as parallel threaded ftp
        parallel_ftp(args)
