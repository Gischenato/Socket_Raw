from socket import *
from socket import socket, AF_PACKET, SOCK_RAW
serverPort = 12000
serverSocket = socket(AF_PACKET, SOCK_RAW)
serverSocket.bind(('eth0', serverPort))
print ("The server is ready to receive")
while True:
    print('-')
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode().upper()
    print(modifiedMessage)
    # serverSocket.sendto(modifiedMessage.encode(), clientAddress)