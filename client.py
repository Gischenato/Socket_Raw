from socket import socket, AF_INET, SOCK_DGRAM
import threading

USER_SOCKET = socket(AF_INET, SOCK_DGRAM)
SERVER_ADDR = ('172.20.32.1', 12000)
USER_SOCKET.settimeout(1)

generate_message = lambda data: f'[{", ".join(data)}]'

def send_message(msg):
    msg = generate_message(msg)
    # print(f'sending {msg} to {SERVER_ADDR}')
    USER_SOCKET.sendto(msg.encode(), SERVER_ADDR)

def login(username):
    send_message(['login', username])

def logout(username):
    send_message(['logout', username])

def private_message(username, message):
    # print('--- private message ----')
    send_message(['pm', username, message])

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