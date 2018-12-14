from multiprocessing import Process, Manager
import socket
import sys
import re

c = int(sys.argv[1])

# some global variables that we will probably need to use
cookies = ["PHPSESSID=1601490688117265152d332-7bf7-49bd-ba61-30f1b6ea3dfa",
           "PHPSESSID=2703122372198558d80bad1-242c-4b1e-b27f-172b7d3fd87c",
           "PHPSESSID=16707226660380076cffb53-4905-467d-b40d-5a5c003567a7"
] # keep track of cookies
visisted = set() # keep track of visited URLs


server = 'eychtipi.cs.uchicago.edu'
port = 80
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_address = (server, port)
sock.connect(serv_address)

# the slash is neccessary
msg1 = 'GET /60gmobile/sigcomm-beam3d-slides.pdf HTTP/1.0\r\n'
msg2 = 'Host: %s\r\n' % server
msg3 = 'Cookie: %s\r\n' % cookies[c]
msg = msg1 + msg2 + msg3 + '\r\n'

sock.sendall(msg.encode())

data = b''
tmp = sock.recv(16384)
data += tmp
while len(tmp):
    tmp = sock.recv(16384)
    data += tmp

sock.close()

# need to parse the data somehow and save it
data = data.split(b'\r\n\r\n')
headers = data.pop(0)
data = b'\r\n\r\n'.join(data)
print(headers)
# f = open('index.html', 'wb')
# f.write(data)
# f.close()
# data = data.decode()
# p_href = 'href="(\S+)"'
# p_HREF = 'HREF="(\S+)"'
# p_src = 'src="(\S+)"'
#
#
# links_href = re.findall(p_href, data)
# links_HREF = re.findall(p_HREF, data)
# links_src = re.findall(p_src, data)

'''
GET /60gmobile/sigcomm-beam3d-slides.pdf HTTP/1.1
Host: eychtipi.cs.uchicago.edu
Cookie: PHPSESSID=16707226660380076cffb53-4905-467d-b40d-5a5c003567a7
Connection: keep-alive
'''
