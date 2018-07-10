import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
BUFFER_SIZE = 2 ** 10
f = open("sample","r")
MESSAGE = f.read()

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(MESSAGE.encode(), (SERVER_HOST, SERVER_PORT))

    flag = 0 #avalin bar
    while True:
        dataproxy, address = client_socket.recvfrom(BUFFER_SIZE)

        ###retrieve control bits
        contolline = dataproxy.splitlines()[0]
        contolline = contolline.decode()
        contolbits = contolline.split(";")
        f = contolbits[0].split("=")[1]
        seq = contolbits[1].split("=")[1]

        ###remove first line of dataproxy -> control bits
        datatmp = []
        n = False
        h = "\r\n".encode()
        for line in dataproxy.splitlines():
            if n:
                datatmp.append(line+h)
            n = True

        if flag == 0 :

            data = bytearray().join(datatmp)

            responseCode = data.decode().splitlines()[0].split(" ")[1]


            if responseCode == '302' or responseCode == "301":
                newURL = data.decode().splitlines()[2].split("ir")[1]
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
                client_socket.sendto(ack.encode(), (SERVER_HOST, SERVER_PORT))
                print("ack",ack,"sent")

                client_socket.sendto(newMessage.encode(), (SERVER_HOST, SERVER_PORT))
                print("dobare req dadam")
            elif (responseCode == '404'):
                flag = 1
                print("khob ride")
                break
            elif responseCode == '200':
                CL = serverDataLen(data.decode())
                print("*************", CL)
                flag = 2
                datafinal = data
                num = int(seq)
                ack = "seq=" + str(num + 1)
                client_socket.sendto(ack.encode(), (SERVER_HOST, SERVER_PORT))
                print("ack",ack,"sent")

        else:
            data = bytearray().join(datatmp)
            if flag == 1 : #code 301 ya 302 boode va javabi ke alan oomade aviln baste doroste
                CL = serverDataLen(data.decode())
                print("*************", CL)
                flag = 2
                datafinal = data
                num = int(seq)
                ack = "seq=" + str(num + 1)
                client_socket.sendto(ack.encode(), (SERVER_HOST, SERVER_PORT))
                print("ack",ack,"sent")
            if flag == 2: #bastehaye badi
                datafinal = datafinal + data
                num = int(seq)
                ack = "seq=" + str(num + 1)
                client_socket.sendto(ack.encode(), (SERVER_HOST, SERVER_PORT))
                print("ack",ack,"sent")
                if( CL <= len(datafinal)):
                    print(data.decode())
                    break;
			# tmp = data.decode()
			# controlLine = tmp.splitlines()[0]
			# controllist = controlLine.split(";")
			# f = controllist[0].split("=")[1]
			# seq = controllist[1].split("=")[1]
			# newMessage = "ack="+seq+1
			# client_socket.sendto(newMessage.encode(), (SERVER_HOST, SERVER_PORT))

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


if __name__ == '__main__':
	print ("[*] Running UDP client...")
	run_client()
