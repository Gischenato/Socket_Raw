from os import fork, pipe, write, read, close
from socket import *
from sys import argv
import threading

server_ip = argv[1] 
server_port = argv[2] 
SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
SERVER_SOCKET.bind((server_ip, int(server_port)))
print ("The server is ready to receive")

USERS = dict()
USERS_NAMES = dict()

convert_coma = lambda txt: str(txt).replace('%;', ',')

def unpack_message(message):
    data = message.strip('][').split(', ')
    return data

def handle(message, clientAddr):
    print(f'message: {message}')
    print(f'clientAddress: {clientAddr}')
    HANDLER = {
        'login': handle_login,
        'logout': handle_logout,
        'pm': handle_private_message,
        'pmf': handle_private_message_with_file,
        'broadcast': handle_broadcast
    }
    data = unpack_message(message.decode())
    print(f'data: {data}')
    HANDLER[data[0]](data[1:], clientAddr)

def handle_private_message_with_file(broadcast_data, clientAddr):
    global USERS, USERS_NAMES
    print(broadcast_data, clientAddr)
    sender = USERS_NAMES[clientAddr]
    receiver = broadcast_data[0]
    message = convert_coma(broadcast_data[1])
    if (receiver in USERS):
        print(f'message: "{message}" to {receiver}')
        newMsg = f'[{sender}] {message}'
        respond(newMsg, USERS[receiver])
    else:
        print(f'user {receiver} not logged in')
        respond(f'user {receiver} not logged in', clientAddr)

def handle_private_message(broadcast_data, clientAddr):
    global USERS, USERS_NAMES
    print(broadcast_data, clientAddr)
    sender = USERS_NAMES[clientAddr]
    receiver = broadcast_data[0]
    message = convert_coma(broadcast_data[1])
    if (receiver in USERS):
        print(f'message: "{message}" to {receiver}')
        newMsg = f'[{sender}] {message}'
        respond(newMsg, USERS[receiver])
    else:
        print(f'user {receiver} not logged in')
        respond(f'user {receiver} not logged in', clientAddr)

def handle_broadcast(broadcast_data, clientAddr):
    global USERS, USERS_NAMES
    sender = USERS_NAMES[clientAddr]
    message = broadcast_data[0]
    newMsg = f'[{sender}] {message}'
    for user in USERS:
        respond(newMsg, USERS[user])

def handle_login(login_data, clientAddr):
    global USERS, USERS_NAMES
    print(f'login_data: {login_data}')
    print(f'clientAddr: {clientAddr}')
    print('users', USERS)
    print('users_names', USERS)
    username = login_data[0]
    if (username in USERS):
        print(f'user already logged in')
        respond('user already logged in', clientAddr)
    else:
        USERS[username] = clientAddr
        USERS_NAMES[clientAddr] = username
        print(f'{username} logged in')
        respond('login success', clientAddr)
        print(USERS)

def handle_logout(logout_data, clientAddr):
    global USERS
    username = logout_data[0]
    if (username in USERS):
        del USERS[username]
        print(f'{username} logged out')
        print(USERS)
        respond('logout success', clientAddr)
    else:
        print(f'user not logged in')
        respond('user not logged in', clientAddr)

def respond(message, clientAddr):
    SERVER_SOCKET.sendto(message.encode(), ('172.31.219.151', clientAddr))

def child_process(clientSocket, clientAddress):
        print("Waiting for a connection...")
        print(f"Accepted connection from {clientAddress}")
        handle(clientSocket.recvfrom(2048)[0], clientAddress[1])
        clientSocket.close()

SERVER_SOCKET.listen(1)
SERVER_SOCKET.settimeout(2)

r, w = pipe()

while True:
    try:
        clientSocket, clientAddress = SERVER_SOCKET.accept()
        child_pid = fork()

        if child_pid == 1:
            close(r)
            write(w, USERS)
            child_process(clientSocket, clientAddress)

        else:
            close(w)



    except KeyboardInterrupt:
        break
    except timeout:
        print('deu timeout')
        pass
