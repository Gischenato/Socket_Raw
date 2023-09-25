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

def handle(message, clientAddr, tcp_socket=None):
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
    HANDLER[data[0]](data[1:], clientAddr, tcp_socket)

def handle_private_message_with_file(broadcast_data, clientAddr, tcp_socket=None):
    global USERS, USERS_NAMES
    print(broadcast_data, clientAddr)
    sender = USERS_NAMES[clientAddr]
    receiver = broadcast_data[0]
    message = convert_coma(broadcast_data[1])
    if (receiver in USERS):
        print(f'message: "{message}" to {receiver}')
        newMsg = f'[{sender}] {message}'
        respond(newMsg, USERS[receiver], tcp_socket)
    else:
        print(f'user {receiver} not logged in')
        respond(f'user {receiver} not logged in', clientAddr, tcp_socket)

def handle_private_message(broadcast_data, clientAddr, tcp_socket=None):
    global USERS, USERS_NAMES
    print(broadcast_data, clientAddr)
    sender = USERS_NAMES[clientAddr]
    receiver = broadcast_data[0]
    message = convert_coma(broadcast_data[1])
    if (receiver in USERS):
        print(f'message: "{message}" to {receiver}')
        newMsg = f'[{sender}] {message}'
        respond(newMsg, USERS[receiver], tcp_socket)
    else:
        print(f'user {receiver} not logged in')
        respond(f'user {receiver} not logged in', clientAddr, tcp_socket)

def handle_broadcast(broadcast_data, clientAddr, tcp_socket=None):
    global USERS, USERS_NAMES
    sender = USERS_NAMES[clientAddr]
    message = broadcast_data[0]
    newMsg = f'[{sender}] {message}'
    for user in USERS:
        respond(newMsg, USERS[user], tcp_socket)

def handle_login(login_data, clientAddr, tcp_socket=None):
    global USERS, USERS_NAMES
    print(f'login_data: {login_data}')
    print(f'clientAddr: {clientAddr}')
    print('users', USERS)
    print('users_names', USERS)
    username = login_data[0]
    if (username in USERS):
        print(f'user already logged in')
        respond('user already logged in', clientAddr, tcp_socket)
    else:
        USERS[username] = clientAddr
        USERS_NAMES[clientAddr] = username
        print(f'{username} logged in')
        respond('login success', clientAddr, tcp_socket)
        print(USERS)

def handle_logout(logout_data, clientAddr, tcp_socket=None):
    global USERS
    username = logout_data[0]
    if (username in USERS):
        del USERS[username]
        print(f'{username} logged out')
        print(USERS)
        respond('logout success', clientAddr, tcp_socket)
    else:
        print(f'user not logged in')
        respond('user not logged in', clientAddr, tcp_socket)

def respond(message, clientAddr, tcp_socket=None):
    print(f'responding {message} to {clientAddr}')
    print('tcp_socket: ', tcp_socket)
    if (tcp_socket):
        tcp_socket.send(message.encode())
    else:
        SERVER_SOCKET.sendto(message.encode(), (server_ip, clientAddr))

def child_process(clientSocket: socket, clientAddress):
    print(f"Accepted connection from {clientAddress}")
    clientSocket.settimeout(2)
    print('------------------------')
    print(clientAddress)
    print(clientSocket)
    print('------------------------')
    while(True):
        try:
            msg = clientSocket.recv(1024)
            handle(msg, clientAddress[1], clientSocket)
        except timeout:
            # print(f'timeout {clientAddress}')
            if not threading.main_thread().is_alive(): break
    clientSocket.close()
              

SERVER_SOCKET.listen(1)
SERVER_SOCKET.settimeout(2)

threads = list()

while True:
    try:
        clientSocket, clientAddress = SERVER_SOCKET.accept()

        x = threading.Thread(target=child_process, args=(clientSocket, clientAddress))
        x.start()
        threads.append(x)

    except KeyboardInterrupt:
        break
    except timeout:
        # print('deu timeout')
        pass
