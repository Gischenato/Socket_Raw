from socket import *
from socket import socket, AF_INET, SOCK_DGRAM
serverPort = 12000
SERVER_SOCKET = socket(AF_INET, SOCK_DGRAM)
SERVER_SOCKET.bind(('172.20.32.1', serverPort))
print ("The server is ready to receive")

USERS = dict()

def unpack_message(message):
    data = message.strip('][').split(', ')
    return data

def handle(message, clientAddr):
    HANDLER = {
        'login': handle_login,
        'logout': handle_logout,
        'bind': handle_bind,
        'pm': handle_private_message,
        'broadcast': handle_broadcast
    }
    data = unpack_message(message.decode())
    print(data, clientAddr)
    HANDLER[data[0]](data[1:], clientAddr)

def handle_private_message(broadcast_data, clientAddr):
    global USERS
    receiver = broadcast_data[0]
    message = broadcast_data[1]
    if (receiver in USERS):
        print(f'message: "{message}" to {receiver}')
        respond(message, USERS[receiver])
    else:
        print(f'user {receiver} not logged in')
        respond(f'user {receiver} not logged in', clientAddr)

def handle_bind(bind_data, clientAddr):
    global USERS
    username = bind_data[0]
    if (username not in USERS):
        respond('cant bind to this user', clientAddr)
    else:
        USERS[username] = clientAddr
        print(f'{username} binded')
        respond('bind success', clientAddr)
    pass

def handle_broadcast(broadcast_data, clientAddr):
    global USERS
    for user in USERS:
        respond(broadcast_data, USERS[user])

def handle_login(login_data, clientAddr):
    global USERS
    username = login_data[0]
    if (username in USERS):
        print(f'user already logged in')
        respond('user already logged in', clientAddr)
    else:
        USERS[username] = clientAddr
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
    SERVER_SOCKET.sendto(message.encode(), clientAddr)

while True:
    print('-------------------')
    handle(*SERVER_SOCKET.recvfrom(2048))