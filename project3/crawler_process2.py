from multiprocessing import Process, Queue, Array
from checks import *
import socket
import time
import sys
import random


def crawler_process(process_states, link_queue, visited, args, p_index):
    '''
    a single crawler process

    inputs:
        process_states (Array)
        link_queue (Queue)
        visited (dict)
        args (namespace)
        p_index (int)
    '''
    process_states[p_index] = 1
    cookie = [None]
    t = random.randint(5, 20)
    t_min = 0
    t_max = 60
    first_run = True

    while 1:
        link = None
        try:
            # try to get a link from the queue
            link = link_queue.get_nowait()
        except:
            # looks like the queue was empty
            # this process is not working anymore
            process_states[p_index] = 0
            # check everyone elses flag
            if sum(process_states) == 0:
                # everyone is doing nothing
                # go back home
                print('-----PROCESS %d GOING HOME-----' % p_index)
                return
            # sleep for a bit
            # print('PROCESS: %d STATE: %d' % (p_index, sum(process_states)))
            time.sleep(0.1)
        # if we got a page process it
        if link:
            print('PROCESS: %d GOT LINK: %s' % (p_index, link))
            if cookie[0]:
                print('PROCESS: %d USING COOKIE' % p_index)
            # we are working
            process_states[p_index] = 1
            # work on the link
            status = work_on_link(link, cookie, link_queue, visited, args)
            if status == 1:
                # something went wrong
                # t = (t + random.uniform(1, 5)) * random.uniform(1, 2)
                # t = min(t_max, t)
                if first_run:
                    # failed on the first run
                    print('-----PROCESS %d GOING HOME-----' % p_index)
                    return
            elif not status:
                # successful
                # t = max(t_min, t - random.uniform(1, 5))
                pass
            elif status == 2:
                # 404 error
                pass
            # after working sleep to prevent rate limit
            # NOTE: no longer needing to sleep as the crawler will
            #       abandon the cookie if it gets rate limited
            # print('PROCESS: %d SLEEPING: %d' % (p_index, t))
            first_run = False
            time.sleep(random.uniform(1, 2))

    return


def work_on_link(link, cookie, link_queue, visited, args):
    '''
    get response from a link and extract links if appropriate
    '''
    # super hack!
    if '.pdf' in link:
        time.sleep(0)
    # initialize socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_address = (args.hostname, args.port)
    try:
        sock.connect(serv_address)
    except:
        print('ERROR: Cannot connect to server', file=sys.stderr)
        link_queue.put(link)
        return 1
    # set up message to send to server
    page = '/' + link
    msg1 = 'GET %s HTTP/1.0\r\n' % page
    msg2 = 'Host: %s\r\n' % args.hostname
    msg3 = ''
    if cookie[0]:
        msg3 = 'Cookie: %s\r\n' % cookie[0]
    msg = msg1 + msg2 + msg3 + '\r\n'
    # send the message
    try:
        sock.sendall(msg.encode())
    except:
        print('ERROR: Cannot send msg to server', file=sys.stderr)
        link_queue.put(link)
        return 1
    # receive the message
    buffer = 16384
    data = b''
    tmp = sock.recv(buffer)
    data += tmp
    while len(tmp):
        tmp = sock.recv(buffer)
        data += tmp
    # parse the received bytes
    headers, data, code = check_parse(data)
    if code != 200:
        print('ERROR: %d LINK: %s' % (code, page))
        # some error, link is ok depending on code...
        if code == 404:
            # page does not exist
            print('THROWING AWAY: %s' % page)
            # sys.exit(1) # need to fix this later
            return 2
        if code == 402:
            # rate limit error
            # abandon the cookie and get a new one on a new request
            cookie[0] = None
        # will need to double check this so we do not go into inf loop
        print('PUTTING BACK: %s' % page)
        link_queue.put(link)
        # sys.exit(1) # need to fix this later
        return 1
    # proceed if every thing is OK
    # save the file
    filename = check_filename(page, args)
    f = open(filename, 'wb')
    f.write(data)
    f.close()
    print('WROTE FILE: %s' % filename)
    # check if we need to parse for more urls
    if check_cont(page):
        # look for more urls
        check_urls(data, link_queue, visited, page)
    # finally set the cookie if there was no cookie before
    if not cookie[0]:
        cookie[0] = check_cookie(headers)
    return 0
