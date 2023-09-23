from socket import socket, AF_INET, SOCK_STREAM 
import threading
from sys import argv
import base64

server_ip = argv[1] 
server_port = argv[2] 
USER_SOCKET = socket(AF_INET, SOCK_STREAM)
SERVER_ADDR = (server_ip, int(server_port))
USER_SOCKET.connect(SERVER_ADDR)
USER_SOCKET.settimeout(1)

generate_message = lambda data: '[' + ", ".join(list(map(replace_coma, data))) + ']'

replace_coma = lambda txt: str(txt).replace(',', '%;')

def generate_file_message(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    return base64.b64encode(content)

def send_message(msg):
    if msg[0] == "pmf": 
        msg = generate_file_message(msg[2])
        USER_SOCKET.sendto(msg, SERVER_ADDR) # base 64

    msg = generate_message(msg)
    USER_SOCKET.sendto(msg.encode(), SERVER_ADDR) # encode utf-8

    print(f'sending {msg} to {SERVER_ADDR}')

def login(username):
    send_message(['login', username])

def logout(username):
    send_message(['logout', username])

def private_message(username, message):
    # print('--- private message ----')
    send_message(['pm', username, message])

def private_message_with_file(username, file):
    send_message(['pmf', username, file])


def broadcast_message(message):
    # print('----- broadcasting -----')
    send_message(['broadcast', message])

def handle_user_input():
    msg = input()
    if (msg.startswith('/')):
        msg = msg[1:].split(' ')
        if (msg[0] == 'exit'): return -1
        elif (msg[0] == 'pm'):
            private_message(msg[1], ' '.join(msg[2:]))
        elif (msg[0] == 'pmf'):
            private_message_with_file(msg[1], ' '.join(msg[2:]))
        elif (msg[0] == 'help'):
            print('private message           -> /pm [user] <message>')
            print('private message with file -> /pmf [user] <file>')
        return 0
    broadcast_message(msg)
    return 0

def thread_listen():
    while True:
        try:
            message, _ = USER_SOCKET.recvfrom(2048)
            message = message.decode()
            print('<msg> ' + message)
        except:
            if not threading.main_thread().is_alive(): break

def main():
    username = input('Enter your username: ')
    login(username)
    x = threading.Thread(target=thread_listen)
    x.start()
    while True:
        if(handle_user_input() == -1): break
    logout(username)

main()
