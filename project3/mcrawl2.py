from multiprocessing import Process, Queue, Array, Manager
from crawler_process2 import *
import argparse
import os
import sys



parser = argparse.ArgumentParser(description="High Throughput Web Crawler",
                                 add_help=False)
parser.add_argument('-v', '--version', action='version',
                                       version='%(prog)s 0.1 maxliu')
parser.add_argument('-n', '--threads', help='number of maximum threads your \
                                             crawler can spawn to perform a \
                                             cooperative crawl',
                                       type=int,
                                       default=1,
                                       dest='max_threads')
parser.add_argument('-h', '--hostname', help='hostname of the server to crawl \
                                              data from',
                                        dest='hostname')
parser.add_argument('-p', '--port', help='port number on the server where the \
                                          web server is running',
                                    type=int,
                                    default=80,
                                    dest='port')
parser.add_argument('-f', '--file', help='local directory to host the \
                                          downloaded files',
                                    default='.',
                                    dest='directory')


def process_args(args):
    '''
    takes the user inputs and checks that everything is ok
    will create a new directory if the specified directory does not exist
    '''
    # need to have more than 0 threads
    if args.max_threads <= 0:
        print('ERROR: Must have at least 1 thread', file=sys.stderr)
        sys.exit(1)
    # check that we have a hostname and reformat the hostname
    if not args.hostname:
        print('ERROR: Must specify a hostname', file=sys.stderr)
        sys.exit(1)
    args.hostname = args.hostname.strip('/')
    args.hostname = args.hostname.split('://')[-1]
    # now check the directory name
    args.directory = args.directory.strip('/') + '/'
    if os.path.isdir(args.directory):
        # directory exists so we will write to it
        if args.directory == './':
            print('Writing all files to the current directory')
        else:
            # remove everything from the specified directory
            for f in os.listdir(args.directory):
                os.remove(args.directory + f)
    else:
        print('Specified directory does not exist')
        print('\tCreating the directory: %s' % args.directory)
        try:
            os.makedirs(args.directory)
        except:
            print('\tERROR: Failed to create the directory', file=sys.stderr)
            sys.exit(1)

    return


if __name__ == '__main__':
    args = parser.parse_args()
    process_args(args)

    #  0 -> process is not doing anything
    #  1 -> process is working
    process_states = Array('i', [0] * args.max_threads)
    link_queue = Queue()
    visited = Manager().dict()
    processes = []

    # add one thing to the queue
    link_queue.put('index.html')
    visited['index.html'] = True

    # start all of the processes
    for i in range(args.max_threads):
        print('Creating and starting process %d' % i)
        p = Process(target=crawler_process,
                    args=(process_states, link_queue, visited, args, i))
        p.start()
        processes.append(p)

    # bring them back
    for p in processes:
        p.join()
