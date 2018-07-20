import math
import argparse
import signal
import logging
import select
import socket
import time
import threading
import re
import hashlib

FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger()

LOCAL_DATA_HANDLER = lambda x:x
REMOTE_DATA_HANDLER = lambda x:x

BUFFER_SIZE = 2 ** 10  # 1024. Keep buffer size as power of 2.


def serverDataLen(s):
    lines = s.splitlines()
    for line in lines:
        left, sep, right = line.partition("Content-Length:")
        print("[-*-] :", line, sep)
        if len(sep) > 0:
            return int(right.strip())
            # if "Content-Length:" in line:
            #     list = line.split(":")
            #     res = list[1].lstrip()
            #     return res
    return -1

def fragmentation(data):
    tmp = []
    i = 0
    n = math.ceil(len(data)/500)
    for i in range (0,n):
        if i == n - 1 and n != 1 :
            tmp.append(data[i*500:])

        else:
            tmp.append(data[i * 500:(i + 1) * 500])

    f = 0
    seq = 0
    fragments = []
    if len(tmp) == 1:
        f = 0
        seq = 0
    for i in range(len(tmp)):
        if len(tmp) == 1:
            f = 0
            seq = 0
        elif i == len(tmp)-1 and len(tmp)!=1:
            f=2
            seq=i
        else:
            f=1
            seq=i

        alireza = ("f="+str(f)+";seq="+str(seq)+";\r\n").encode()
        proxychecksum = ("checksum=" + str(hashlib.md5(alireza + tmp[i]).hexdigest()) + ";\r\n").encode()
        # print(len(proxychecksum))
        fragment = proxychecksum+alireza+tmp[i]

        # print(len(fragment),len(proxychecksum),len(alireza),len(tmp[i]))

        fragments.append(fragment)

    # data = bytearray().join(tmp)
    # data = data.split("\r\n\r\n".encode())[1]
    # file = open("index.jpg", "wb")
    # file.write(data)
    return fragments




def retreiveHostname(dataClient):
    data = dataClient.decode()
    #print(data)
    second = data.splitlines()[1]
    list2 = second.split(":")
    hostname = list2[1].lstrip()
    dst = socket.gethostbyname(hostname) + ":80"
    server_address = ip_to_tuple(dst)
    return server_address

def check_ack(ack):

    acknum = ack.decode().split("=")[1]
    return int(acknum)


def check_isack(data):
    data = data.decode()
    line = data.splitlines()[0]
    left, sep, right = line.partition("seq=")
    if len(sep) > 0:
        return int(right.strip())
    else:
        return -1

def udpCache(dataInter , dataServer):
    #har do vorodi bytearray hastan

    fileName = hashlib.md5(dataInter.strip()).hexdigest()

    file = open("records","a+")
    file.write(fileName+"\n")

    record = open(fileName,"wb")
    record.write(dataServer)

def searchCache(dataClient):

    file = open("records", "r")
    records = file.readlines()

    print("req client : ",hashlib.md5(dataClient.strip()).hexdigest(),type(hashlib.md5(dataClient.strip()).hexdigest()),len(hashlib.md5(dataClient.strip()).hexdigest()))

    for line in records:
        print("line is : ",line,type(line.strip()),len(line.strip()))
        if hashlib.md5(dataClient.strip()).hexdigest() == line.strip():
            record = open(line.strip() , "rb")
            print("*************haha chace works :))))))")
            return record.read()

    return udp_server( dataInter = dataClient)


def udp_client(client_socket):
    client_address = None
    flag = 0
    while True:
        try:
            dataClient, address = client_socket.recvfrom(BUFFER_SIZE)
            #khate aval ke checjsum hast ro barresi va joda mikonim
            clientChecksum = dataClient.splitlines()[0].decode().split(";")
            clientChecksum_value = clientChecksum[0].split("=")[1]

            dataClient = dataClient[44:]

            proxyChecksum =  hashlib.md5(dataClient).hexdigest()

            if(clientChecksum_value != proxyChecksum ):
                print("ride")
                continue

        except socket.timeout:
            if (flag == 1 ):
                print("time out happend unfortuently negro")
                client_socket.sendto(frags[counter], client_address)
            continue
        flag = 1
        print("came from client : ",dataClient.decode())
        if (client_address == None or address != client_address):
            client_address = address
        if check_isack(dataClient) >= 0  :

            if( check_ack(dataClient) < len(frags) ):
                counter = check_ack(dataClient)
                client_socket.sendto(frags[counter], client_address)
                print("frag sent to client : ", counter)

            if ((len(frags)) == check_ack(dataClient) ):
                print("gav")
                counter = 0
                flag = 0
        else:
            ackProxy = make_ack()
            client_socket.sendto(ackProxy, client_address)


            dataServer = searchCache(dataClient)

            print("[*] fragmantation is starting ...")
            frags = fragmentation(dataServer)
            num_frag = len(frags)
            print("[*] number of frags: " , num_frag)
            counter = 0
            client_socket.sendto(frags[counter], client_address)

            print("frag sent to client : ", counter)

        #lots of things to do
        #client_socket.sendto(dataServer, client_address)


def make_ack():
    alireza = ("f="+str(3)+";seq="+str(1)+";\r\n").encode()
    proxychecksum = ("checksum=" + str(hashlib.md5(alireza).hexdigest()) + ";\r\n").encode()
    return proxychecksum+alireza

def udp_server(dataInter = None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = retreiveHostname(dataInter)
    server_socket.connect(server_address)
    server_socket.settimeout(100)

    server_socket.send(dataInter)

    dataFinalarray = b''
    while True:
        try:
            dataServer = server_socket.recv(BUFFER_SIZE)


            if not dataServer :

                udpCache(dataInter,dataFinalarray)

                server_socket.close()
                return dataFinalarray


            if  '301 Moved Permanently'.encode() in dataServer or '302 Found'.encode() in dataServer or '404 Not Found'.encode() in dataServer :
                udpCache(dataInter, dataServer)
                server_socket.close()
                return dataServer
            else:

                if '200 OK'.encode() in dataServer:

                    dataFinalarray = bytearray(dataServer)
                    print("*******")
                else :
                    # if "</html>" in str(dataServer):
                    #     print(dataServer)
                    #     server_socket.close()
                    #     index = dataServer.decode("utf-8","ignore").index('</html>')
                    #     dataServer = (dataServer.decode("utf-8","ignore")[:index + len('</html>')]).encode()
                    #     dataFinalarray = dataFinalarray + bytearray(dataServer)
                    #     return dataFinalarray
                    # if not dataServer:
                    #     return dataFinalarray
                    # else:
                    dataFinalarray = dataFinalarray + bytearray(dataServer)
            # if len(dataServer) < BUFFER_SIZE:
            #     server_socket.close()
            #     return dataFinalarray
        except socket.timeout:
            server_socket.send(dataInter)
            # server_socket.close()
            # return dataFinalarray





def udp_proxy(src):
    """Run UDP proxy.

    Arguments:
    src -- Source IP address and port string. I.e.: '127.0.0.1:8000'
    dst -- Destination IP address and port. I.e.: '127.0.0.1:8888'
    """
    LOGGER.debug('Starting UDP-to_TCP proxy...')
    LOGGER.debug('Src: {}'.format(src))
    # LOGGER.debug('Dst: {}'.format(dst))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(ip_to_tuple(src))
    client_socket.settimeout(1)
    udp_client(client_socket)





def tcp_proxy(src, dst):
    """Run TCP proxy.

    Arguments:
    src -- Source IP address and port string. I.e.: '127.0.0.1:8000'
    dst -- Destination IP address and port. I.e.: '127.0.0.1:8888'
    """
    LOGGER.debug('Starting TCP_to_UDP proxy...')
    LOGGER.debug('Src: {}'.format(src))
    LOGGER.debug('Dst: {}'.format(dst))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.bind(ip_to_tuple(src))
    client_socket.listen(1)
    conn, addr = client_socket.accept()
    server_address = ip_to_tuple(dst)
    global client_address
    client_address = addr

    def client(server_address):
        print("alireza")
        while True:
            dataClient = conn.recv(BUFFER_SIZE)
            print(dataClient.decode())
            server_socket.sendto(dataClient,server_address)
            thread5 = threading.Thread(target = server, args=(client_address,)).start()

    def server(client_address):
        while True:
            data, address = server_socket.recvfrom(BUFFER_SIZE)
            conn.sendall(data)
            break;
    thread4 = threading.Thread(target= client , args=(server_address,)).start()

    LOGGER.debug('Looping proxy (press Ctrl-Break to stop)...')
# end-of-function tcp_proxy








def ip_to_tuple(ip):
    """Parse IP string and return (ip, port) tuple.

    Arguments:
    ip -- IP address:port string. I.e.: '127.0.0.1:8000'.
    """
    ip, port = ip.split(':')
    return (ip, int(port))
# end-of-function ip_to_tuple


def main():
    """Main method."""
    parser = argparse.ArgumentParser(description='TCP/UPD proxy.')

    # TCP UPD groups
    proto_group = parser.add_mutually_exclusive_group(required=True)
    proto_group.add_argument('--tcp', action='store_true', help='TCP proxy')
    proto_group.add_argument('--udp', action='store_true', help='UDP proxy')

    parser.add_argument('-s', '--src', required=True, help='Source IP and port, i.e.: 127.0.0.1:8000')
    parser.add_argument('-d', '--dst', required=False, help='Destination IP and port, i.e.: 127.0.0.1:8888')

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-q', '--quiet', action='store_true', help='Be quiet')
    output_group.add_argument('-v', '--verbose', action='store_true', help='Be loud')

    args = parser.parse_args()

    if args.quiet:
        LOGGER.setLevel(logging.CRITICAL)
    if args.verbose:
        LOGGER.setLevel(logging.NOTSET)

    if args.udp:
        udp_proxy(args.src)
    elif args.tcp:
        tcp_proxy(args.src, args.dst)
# end-of-function main


if __name__ == '__main__':
    main()