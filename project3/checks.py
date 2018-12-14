import time
import os
import re


def check_filename(page, args):
    '''
    return back the name of the file to write to
    '''
    filename = page.split('/')[-1]
    if len(filename) == 0:
        filename = page.split('/')[-2]
        filename += '.html'
    path = args.directory + filename
    if os.path.isfile(path):
        # print('FOUND SAME NAMED FILE %s-----------------' % filename)
        # need to change the name
        # t = str(int(time.time()))
        # assume that format of file is xxxxx.xxx
        # or the format is xxxxx-x.xxx
        # filename = filename.split('.')
        # filename = filename[0] + '-' + t + '.' + filename[1]
        cont = True
        while cont:
            p = '-([0-9]+).'
            n = re.findall(p, filename)
            if len(n) == 0:
                filename = filename.split('.')
                filename = filename[0] + '-1' + '.' + filename[1]
            else:
                old = '-' + n[0] + '.'
                new = '-' + str(int(n[0]) + 1) + '.'
                filename = filename.replace(old, new)
            # print('NEW FILE NAME %s' % filename)
            tmp = args.directory + filename
            if not os.path.isfile(tmp):
                cont = False

    filename = args.directory + filename

    return filename


def check_cont(page):
    '''
    given a page do we need to look for urls in it
    '''
    filename = page.split('/')[-1]
    if '.html' in filename:
        return True
    elif '.htm' in filename:
        return True
    else:
        return False


def check_cookie(headers):
    '''
    returns cookie back from response header
    '''
    p = '(PHPSESSID=\S+);'
    cookie = re.findall(p, headers)[0]

    return cookie


def check_response_code(headers):
    '''
    check is response code is ok
    '''
    p = 'HTTP/1.1 ([0-9]+)'
    code = int(re.findall(p, headers)[0])

    return code


def check_parse(data):
    '''
    given the byte response from the http server we need to parse it and
    check if our request was ok
    '''
    # assuming that we are still going to have to split by '\r\n'
    data = data.split(b'\r\n\r\n')
    headers = data.pop(0).decode()
    data = b'\r\n\r\n'.join(data)
    code = check_response_code(headers)

    return headers, data, code


def check_urls(data, link_queue, visited, page):
    '''
    given a page, find all of the urls and check if we have visited them yet,
    if not we will need to add them to the queue
    '''
    data = data.decode()
    # regex patterns to find urls
    p_href = 'href="(\S+)"'
    p_HREF = 'HREF="(\S+)"'
    p_src = 'src="(\S+)"'

    links_href = re.findall(p_href, data)
    links_HREF = re.findall(p_HREF, data)
    links_src = re.findall(p_src, data)
    links = links_href + links_HREF + links_src

    for link in links:
        if '..' in link:
            print(page)
            print(link)
        # check if its external
        if '://' in link:
            # external
            pass
        elif link[0] == '#':
            # not a link
            pass
        else:
            if link[0] == '.':
                # is a relative path
                # print(page)
                # print(link)
                rel = '/'.join(page.split('/')[1:-1])
                link = rel + link.strip('.')[1:]
                # print(link)
                # print('---')
                # print(page)
                # print(link)
                # print('---')
            elif link[0] != '/':
                # this is also a relative path
                # print(page)
                # print(link)
                rel = '/'.join(page.split('/')[1:-1])
                if len(rel) != 0:
                    link = rel + '/' + link
                # print(page)
                # print(link)
            # check if we have seen link before
            if visited.get(link, False):
                # we have seen it
                # print('DO NOT PUT: %s' % link)
                pass
            else:
                # print('ADDED: %s' % link)
                link_queue.put(link)
                visited[link] = True
                # print('---')
                # print(page)
                # print(link)
                # print('---')
