import socket
import re
import hashlib
from urllib.parse import urlparse

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
BUFFER_SIZE = 2 ** 10
f = open("sample","r")
MESSAGE = f.read()
newMessage=""

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(("checksum=" + str(hashlib.md5(MESSAGE.encode()).hexdigest()) + ";\r\n"+MESSAGE).encode(), (SERVER_HOST, SERVER_PORT))
    client_socket.settimeout(10)
    seqNum = []

    flag = 0 #avalin bar
    flagAckNewMessage = 0 #ack req dovomi hanooz baram nayoomade
    flagAckMessage = 0  # ack req avali hanooz baram nayoomade
    while True:
        try:
            dataproxy, address = client_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("timeout shode!")
            if (flagAckMessage == 0 ):
                client_socket.sendto(("checksum=" + str(hashlib.md5(MESSAGE.encode()).hexdigest()) + ";\r\n"+MESSAGE).encode(), (SERVER_HOST, SERVER_PORT))
            elif (flagAckNewMessage == 0 and flag == 1):
                client_socket.sendto(
                    ("checksum=" + str(hashlib.md5(newMessage.encode()).hexdigest()) + ";\r\n" + newMessage).encode(),(SERVER_HOST, SERVER_PORT))
            elif (flag == 2):
                num = int(len(seqNum))
                ack = "seq=" + str(num + 1)
                client_socket.sendto(
                    ("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n" + ack).encode(),
                    (SERVER_HOST, SERVER_PORT))
                print("*ack", num + 1, "sent")

        #retrive checksum
        checksum_proxy = dataproxy.splitlines()[0].decode().split(";")
        checksum_proxy_Value = checksum_proxy[0].split("=")[1]
        print(checksum_proxy_Value)


        ###retrieve control bits
        contolline = dataproxy.splitlines()[1]
        contolline = contolline.decode()
        contolbits = contolline.split(";")
        f = contolbits[0].split("=")[1]
        seq = contolbits[1].split("=")[1]

        print("frag ",seq," : ",len(dataproxy))

        dataNew = removeControlLines(dataproxy, int(seq))

        dataWOChechsum = removeCkecksum(dataproxy,int(seq))

        clientChecksum = hashlib.md5(dataWOChechsum).hexdigest()

        if (flag==0 and f == '3'):
            print("haha ack req avali oomad")
            flagAckMessage = 1
            continue
        if (flag==1 and f=='3'):
            print("haha ack req dovomi oomad")
            flagAckNewMessage = 1
            continue


        if( clientChecksum != checksum_proxy_Value ):
            "*********kharab bood dobare darkhast dadam"
            num = int(len(seqNum))
            ack = "seq=" + str(num + 1)
            client_socket.sendto(
                ("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n" + ack).encode(),
                (SERVER_HOST, SERVER_PORT))
            print("***ack", num + 1, "sent")
            continue


        if flag == 0 :

            dataFirst = dataNew
            print("len data first : ",len(dataFirst))

            print("datafirst",dataFirst.decode())

            datafirstline = dataFirst.decode().splitlines()[0]

            print("datafirstline",datafirstline)

            if ("302" in datafirstline) or ("301" in datafirstline) :
                responseCode = '302 or 301'
                print("responseCode",responseCode)

                locLine=""

                for line in dataFirst.splitlines():
                    if "Location:".encode() in line:
                        locLine = line.decode()
                        print(locLine)

                newURL = locLine.split(" ")[1].lstrip()
                print(newURL)
                flag = 1
                print("rafte jaye dg tem ya per")
                # change url
                firstLine = MESSAGE.splitlines()[0]
                wordsUrl = firstLine.split(" ")
                wordsUrl[1] = newURL
                newfirstline = " ".join(wordsUrl)
                newMessage = MESSAGE.replace(firstLine, newfirstline)

                for line in newMessage.splitlines() :
                    if "Host:" in line:
                        hostLine = line

                wordsHost = hostLine.split(" ")
                wordsHost[1]= urlparse(newURL).hostname
                newHostLine = " ".join(wordsHost)
                newMessage = newMessage.replace(hostLine, newHostLine)

                print("new req is : ", newMessage)

                num = int(seq)
                ack = "seq=" + str(num + 1)
                client_socket.sendto(
                    ("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n" + ack).encode(),
                    (SERVER_HOST, SERVER_PORT))
                print("ack", ack, "sent")

                client_socket.sendto(
                    ("checksum=" + str(hashlib.md5(newMessage.encode()).hexdigest()) + ";\r\n" + newMessage).encode(),
                    (SERVER_HOST, SERVER_PORT))
                flagAck = 0
                print("dobare req dadam")


                if (f == '2' or f == '0'):
                    seqNum = []
                    continue;

            elif "301".encode() in firstLine:
                responseCode = '301'

            elif "404".encode() in firstLine:
                responseCode = '404'
                flag = 1
                print("khob ride 404 ")
                seqNum = []
                break

            elif "200".encode() in firstLine:
                responseCode = '200'
                data = dataNew
                print("flag = ", flag, "added to data ", seq)

                if int(seq) == len(seqNum):

                    print("hahaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

                    flag = 2

                    datafinal = data
                    seqNum.append(seq)

                    num = int(seq)
                    ack = "seq=" + str(num + 1)
                    client_socket.sendto(
                        ("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n" + ack).encode(),
                        (SERVER_HOST, SERVER_PORT))
                    print("*************ack", num + 1, "sent")

                if (f == '2' or f == '0'):
                    # htmlMaker(datafinal)
                    # print(datafinal.decode())
                    seqNum = []
                    continue;
            else:
                print("code mojaz nist")
                seqNum = []
                break;


        else:
            if flag == 1 : #code 301 ya 302 boode va javabi ke alan oomade aviln baste doroste
                # data = bytearray().join(dataproxy)
                data = dataNew

                if int(seq) == len(seqNum):
                    print("flag = ", flag, "added to data ", seq)
                    flag = 2

                    datafinal = data

                    seqNum.append(seq)

                    num = int(seq)
                    ack = "seq=" + str(num + 1)
                    client_socket.sendto(
                        ("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n" + ack).encode(),
                        (SERVER_HOST, SERVER_PORT))
                    print("ack", num + 1, "sent")

                if (f == '2' or f == '0'):
                    print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",f)
                    # htmlMaker(datafinal)
                    # print(datafinal)
                    # print(datafinal.decode())
                    seqNum = []
                    continue

            if flag == 2: #bastehaye badi
                data = dataNew
                if int(seq) == len(seqNum):
                # if seq not in seqNum:
                    datafinal = datafinal + data
                    seqNum.append(seq)
                    print("added to data ", seq)

                    num = int(seq)
                    ack = "seq=" + str(num + 1)
                    client_socket.sendto(
                        ("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n" + ack).encode(),
                        (SERVER_HOST, SERVER_PORT))
                    print("***ack", num + 1, "sent")

                if( f == '2' or f == '0' ):
                    # print(datafinal)
                    # htmlMaker(datafinal)
                    seqNum = []
                    break;
			# tmp = data.decode()
			# controlLine = tmp.splitlines()[0]
			# controllist = controlLine.split(";")
			# f = controllist[0].split("=")[1]
			# seq = controllist[1].split("=")[1]
			# newMessage = "ack="+seq+1
			# client_socket.sendto(newMessage.encode(), (SERVER_HOST, SERVER_PORT))
def htmlMaker(data):

    # data = data.split("\r\n\r\n".encode())[1]
    # file = open("index.png","wb")
    # file.write(data)

    data = data.split("\r\n\r\n".encode())[1]
    file = open("index.html","w")
    file.write(data.decode("utf-8","ignore"))

# def serverDataLen(s):
#     lines = s.splitlines()
#     for line in lines:
#         left, sep, right = line.partition("Content-Length:")
#         print("[-*-] :", line, sep)
#         if len(sep) > 0:
#             return int(right.strip())
#             # if "Content-Length:" in line:
#             #     list = line.split(":")
#             #     res = list[1].lstrip()
#             #     return res
#     return -1
def removeControlLines(data,seq):
    # lines = data.splitlines()
    # lines = lines[1:]
    # dataNew = bytearray()
    # h = ("\n").encode()
    # for line in lines:
    #     dataNew = dataNew + line + h
    if seq in range(0,10) :
        dataNew = data[12+44:]

    elif seq in range(10,100):
        dataNew = data[13+44:]

    elif seq in range(100,1000):
        dataNew = data[14+44:]

    else:#momkene berine!
        dataNew = data[15 + 44:]

    return dataNew
def removeCkecksum(dataproxy,seq):
    if seq in range(0,10) :
        dataWOchecksum = dataproxy[44:]
    else:
        dataWOchecksum = dataproxy[44:]
    return dataWOchecksum

if __name__ == '__main__':
	print ("[*] Running UDP client...")
	run_client()