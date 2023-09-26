from socket import socket, timeout, AF_INET, SOCK_DGRAM, SOCK_STREAM
import threading
from sys import argv
import base64


generate_message = lambda data: '[' + ", ".join(list(map(replace_coma, data))) + ']'

replace_coma = lambda txt: str(txt).replace(',', '%;')

class Client:
    def __init__(self, server_ip, server_port, socket_type='tcp'):
        self.SOCKET_TYPE = socket_type
        self.SERVER_IP = server_ip
        self.SERVER_PORT = int(server_port)
        self.DATA_SOCKET = socket(AF_INET, SOCK_STREAM) if socket_type == 'tcp' else socket(AF_INET, SOCK_DGRAM)
        self.CONTROLL_SOCKET = socket(AF_INET, SOCK_STREAM) if socket_type == 'tcp' else socket(AF_INET, SOCK_DGRAM)

        self.username = None


    def connect(self):
        print(f'connecting to {self.SERVER_IP}:{self.SERVER_PORT}')
        self.CONTROLL_SOCKET.connect((self.SERVER_IP, self.SERVER_PORT + 2))
        self.DATA_SOCKET.connect((self.SERVER_IP, self.SERVER_PORT + 3))
    
    
    def close(self):
        self.CONTROLL_SOCKET.close()
        self.DATA_SOCKET.close()

    def send_message(self, msg, socket:socket):
        msg = generate_message(msg)
        if self.SOCKET_TYPE == 'tcp':
            socket.send(msg.encode())
        else:
            socket.sendto(msg.encode(), (self.SERVER_IP, self.SERVER_PORT))

    def handle_tcp_socket(self, socket:socket):
        message = socket.recv(1024)
            # if not message:  
        message = message.decode()
        print('<msg> ' + message)

    def handle_udp_socket(self, socket:socket):
        message, _ = socket.recvfrom(2048)
        message = message.decode()
        print('<msg> ' + message)

    def listen(self, socket:socket):
        socket.settimeout(2)
        while True:
            try:
                if self.SOCKET_TYPE == 'tcp':
                    self.handle_tcp_socket(socket)
                else:
                    self.handle_udp_socket(socket)
                pass
            except timeout:
                if not threading.main_thread().is_alive(): break
            except:
                break

    def private_message(self, username, message):
        self.send_message(['pm', username, message], self.DATA_SOCKET)

    def login(self, username):
        self.send_message(['login', username], self.CONTROLL_SOCKET)

    def logout(self, username):
        self.username = None
        self.send_message(['logout', username], self.CONTROLL_SOCKET)
    
    def private_message_with_file(self):
        pass

    def print_help(self):
        pass

    def broadcast_message(self, message):
        self.send_message(['broadcast', message])
        pass


    def handle_user_input(self):
        try:
            msg = input()
        except KeyboardInterrupt:
            print('AQUI')
            return -1
        join_message = lambda msg: ' '.join(msg)
        if (msg.startswith('/')):
            msg = msg[1:].split(' ')
            option = msg[0]
            if (option == 'exit'): return -1
            elif (option == 'pm'): 
                self.private_message(msg[1], join_message(msg[2:]))
            elif (option == 'pmf'): pass
            elif (option == 'help'): pass
            elif (option == 'all'): pass
            elif (option == 'login'):
                self.login(msg[1])
                # self.username = msg[1]
            elif (option == 'logout'): pass
            # else: print('invalid command')
        return 0

    def run(self):
        if (self.SOCKET_TYPE == 'tcp'):
            print('running tcp client')
            self.connect()
        
        threading.Thread(target=self.listen, args=(self.CONTROLL_SOCKET,)).start()
        threading.Thread(target=self.listen, args=(self.DATA_SOCKET,)).start()

        while True:
            if (self.handle_user_input() == -1): break

def main():
    client = Client('172.20.32.1', 12000, 'tcp')
    try:
        client.run()
    except timeout:
        print('teste')
    except KeyboardInterrupt:
        pass
    print('closing client')
    client.close()


main()