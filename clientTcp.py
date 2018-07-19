#!/usr/bin/env python

__author__      = 'Radoslaw Matusiak'
__copyright__   = 'Copyright (c) 2016 Radoslaw Matusiak'
__license__     = 'MIT'
__version__     = '0.1'

import socket
import time

SERVER_HOST = "172.23.189.156"
SERVER_PORT = 8004
BUFFER_SIZE = 2 ** 10

MESSAGE = "type=A server=217.215.155.155 target=aut.ac.ir"
def retreive(msg):
    list=msg.split(" ")
    type = list[0].split("=")[1]
    type = list[1].split("=")[1]

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SERVER_HOST, SERVER_PORT)

    client_socket.connect(server_address)
    client_socket.sendall(MESSAGE.encode())
    while True:

        data = client_socket.recv(BUFFER_SIZE)

        print ('[*] Server ',str(server_address), ' response: ' ,data.decode())

        time.sleep(3)
# end-of-function run_client


if __name__ == '__main__':
    print ( '[*] Running TCP client...')
    run_client()