import socket
import re
import hashlib

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
BUFFER_SIZE = 2 ** 10
f = open("sample","r")
MESSAGE = f.read()

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(len("checksum=" + str(hashlib.md5(MESSAGE.encode()).hexdigest()) + ";\r\n"))
    client_socket.sendto(("checksum=" + str(hashlib.md5(MESSAGE.encode()).hexdigest()) + ";\r\n"+MESSAGE).encode(), (SERVER_HOST, SERVER_PORT))
    client_socket.settimeout(.1)
    seqNum = []

    flag = 0 #avalin bar
    flagAck = 0 #ack req hanooz baram nayoomade
    while True:
        try:
            dataproxy, address = client_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            if (flagAck == 0 ):
                client_socket.sendto(("checksum=" + str(hashlib.md5(newMessage.encode()).hexdigest()) + ";\r\n"+newMessage).encode(), (SERVER_HOST, SERVER_PORT))

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
        if (f == '3'):
            print("haha ack oomad")
            flagAck = 1
            continue

        if( clientChecksum != checksum_proxy_Value ):
            continue


        if flag == 0 :

            dataFirst = dataNew
            print("len data first : ",len(dataFirst))
            responseCode = dataFirst.decode().splitlines()[0].split(" ")[1]


            if responseCode == '302' or responseCode == "301":
                newURL = dataFirst.decode().splitlines()[2].split(".com")[1]
                flag = 1
                print("rafte jaye dg tem ya per")
                # change url
                firstLine = MESSAGE.splitlines()[0]
                words = firstLine.split(" ")
                words[1] = newURL
                newfirstline = " ".join(words)
                newMessage = MESSAGE.replace(firstLine, newfirstline)
                #

                num = int(seq)
                ack = "seq=" + str(num + 1)
                client_socket.sendto(("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n"+ack).encode(), (SERVER_HOST, SERVER_PORT))
                print("ack",ack,"sent")

                client_socket.sendto(("checksum=" + str(hashlib.md5(newMessage.encode()).hexdigest()) + ";\r\n"+newMessage).encode(), (SERVER_HOST, SERVER_PORT))
                flagAck = 0
                print("dobare req dadam")

            elif (responseCode == '404'):
                flag = 1
                print("khob ride")
                break
            elif responseCode == '200':
                data = dataNew
                print("flag = ", flag, "added to data ", seq)

                flag = 2
                datafinal = data
                seqNum.append(seq)

                num = int(seq)
                ack = "seq=" + str(num + 1)
                client_socket.sendto(
                    ("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n" + ack).encode(),
                    (SERVER_HOST, SERVER_PORT))
                print("*************ack", num + 1, "sent")

        else:
            if flag == 1 : #code 301 ya 302 boode va javabi ke alan oomade aviln baste doroste
                # data = bytearray().join(dataproxy)
                data = dataNew
                print("flag = ",flag, "added to data ", seq)

                flag = 2
                datafinal = data
                seqNum.append(seq)

                num = int(seq)
                ack = "seq=" + str(num + 1)
                client_socket.sendto(("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n"+ack).encode(), (SERVER_HOST, SERVER_PORT))
                print("*************ack",num+1,"sent")

            if flag == 2: #bastehaye badi
                if seq not in seqNum:

                    data = dataNew

                    datafinal = datafinal + data
                    seqNum.append(seq)

                    print("added to data ", seq)

                    num = int(seq)
                    ack = "seq=" + str(num + 1)
                    client_socket.sendto(("checksum=" + str(hashlib.md5(ack.encode()).hexdigest()) + ";\r\n"+ack).encode(), (SERVER_HOST, SERVER_PORT))
                    print("***ack", num + 1, "sent")

                if( f == '2' ):
                    htmlMaker(datafinal.decode())
                    # print(datafinal.decode())
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
    start = data.index("<")
    end = data.index("</html>")
    file = open("index.html","w")
    file.write(data[start:end + len("</html>")])

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
def removeControlLines(data,seq):
    # lines = data.splitlines()
    # lines = lines[1:]
    # dataNew = bytearray()
    # h = ("\n").encode()
    # for line in lines:
    #     dataNew = dataNew + line + h
    if seq in range(0,10) :
        dataNew = data[12+44:]
    else:
        dataNew = data[13+44:]
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