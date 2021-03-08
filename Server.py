import argparse
import binascii
import socket
from sys import argv
import struct

#temp host holder
Host = ''
#get the port from aguments given
parser = argparse.ArgumentParser(description="""This is a Server program""")
parser.add_argument('port', type=int, help='this is the port to connect to the server on', action='store')
args = parser.parse_args(argv[1:])
port= args.port

#try and create socket to connect to google DNS server
try:
    google_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print("[S]: Server socket created")
except socket.error as err:
    print('socket open error: {} \n'.format(err))
    exit()

#connect to google DNS server
google_addr = ('8.8.8.8', 53)
google_sock.connect(google_addr)
print('Google connected')

#try and create socket to connect to client
try:
    server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
except socket.err as err:
    print('socket open error: {} \n'.format(err))

#listen and connect to the client trying to connect
server_sock.bind((Host, port))
server_sock.listen(1)
newSock, serverAddress = server_sock.accept()
print('Client connected')

#our code -->
#first while the client and google is connected
while True:
    #retrieve the message (host name) from client
    client_message = newSock.recv(256)
    if(len(client_message) == 0):
        break
    client_message = client_message.decode('utf-8')
    print('CLIENT MSSG RECEIVED: ', client_message)

    #decode the message and then send as UDP packet to google DNS server
    udp_message = client_message.split('.')
    answer = ''
    for sections in udp_message:
        message_length = len(sections)
        if len(sections) < 10:
            message_length = '0' + str(len(sections))
        answer = answer + message_length + ''
        for characters in sections:
            hexcode = format(ord(characters), 'x')
            hexcode = hexcode.upper()
            answer = answer + hexcode + ''
    answer = answer+"0000010001"
    message = "AAAA01000001000000000000" + answer
    print('MESSAGE HEXAFIED: ', message)
    google_sock.sendto(binascii.unhexlify(message), google_addr)
    print('SENT TO GOOGLE SERVER:', binascii.unhexlify(message))
    while True:
        print('sending to udp')
        #then retrieve the answer from google DNS server and decode
        udpOnlineData, addr = google_sock.recvfrom(1024)
        print('LENGTH: ',(udpOnlineData))
        print('RECEIVED FROM GOOGLE SERVER: ', binascii.hexlify(udpOnlineData).decode('utf-8'))
        message = binascii.hexlify(udpOnlineData)

        #decode google answer and convert to decimal form
        decode_message = message[-8:]
        print(message[-8:])
        ans = ' '
        final = [decode_message[i:i+2] for i in range(0, len(decode_message), 2)]
        print('FINAL MESSAGE:', final)
        for x in final:
            x = str(int(x, 16)) + '.'
            ans = ans + x + ''
        print(ans)
        decode_message = ans[:-1]
        print('DECODED MESSAGE: ', decode_message)
        #send send answer back to client (if multiple separate by ',') if none send 'OTHER'
        newSock.sendall(decode_message.encode('utf-8'))
#disconnect from client and google DNS
server_sock.close()
exit()










