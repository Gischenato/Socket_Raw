from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SHUT_RDWR, timeout
import json
import threading

convert_coma = lambda txt: str(txt).replace('%;', ',')

class Users:
    def __init__(self):
        self.data = dict()

    def add(self, username, client_ip, client_port, tcp_socket=None):
        new_user = {
            'socket_type': 'tcp' if tcp_socket else 'udp',
            'client_ip': client_ip,
            'client_port': client_port,
            'tcp_socket': tcp_socket,
            'username': username,
        }
        self.data[username] = new_user
        self.data[(client_ip, client_port)] = new_user

    def remove(self, username):
        ip = self.data[username]['client_ip']
        port = self.data[username]['client_port']
        del self.data[username]
        del self.data[(ip, port)]

    def get(self, user):
        return self.data[user]
    
    def get_socket(self, user):
        return self.data[user]['tcp_socket']

    def get_username(self, user):
        return self.data[user]['username']
    
    # def set_username(self, user, username):
    #     self.data[user]['username'] = username
    
    def get_client_ip(self, user):
        return self.data[user]['client_ip']
    
    def get_client_port(self, user):
        return self.data[user]['client_port']
    
    def get_socket_type(self, user):
        return self.data[user]['socket_type']

    def __contains__(self, user):
        return user in self.data

    def __str__(self):
        return str(self.data)

class Server:
    def __init__(self, host, port):
        self.HOST = host
        self.UDP_CONTROLL_PORT = int(port)
        self.UDP_DATA_PORT = int(port) + 1
        self.TCP_CONTROLL_PORT = int(port) + 2
        self.TCP_DATA_PORT = int(port) + 3

        self.UDP_CONTROLL_SOCKET = socket(AF_INET, SOCK_DGRAM)
        self.UDP_DATA_SOCKET = socket(AF_INET, SOCK_DGRAM)

        self.TCP_CONTROLL_SOCKET = socket(AF_INET, SOCK_STREAM)
        self.TCP_DATA_SOCKET = socket(AF_INET, SOCK_STREAM)
        
        self.TCP_CONTROLL_SOCKET.bind((self.HOST, self.TCP_CONTROLL_PORT))
        self.TCP_DATA_SOCKET.bind((self.HOST, self.TCP_DATA_PORT))
        self.UDP_CONTROLL_SOCKET.bind((self.HOST, self.UDP_CONTROLL_PORT))
        self.UDP_DATA_SOCKET.bind((self.HOST, self.UDP_DATA_PORT))

        self.TCP_CONTROLL_SOCKET.listen(1)
        self.TCP_DATA_SOCKET.listen(1)

        self.USERS = Users()


    def listen_udp(self, socket:socket):
        socket.settimeout(2)
        print(f'listening udp on {socket.getsockname()}')
        while True:
            try:
                socket.recvfrom(2048)
            except:
                if not threading.main_thread().is_alive(): return

    def listen_tcp(self, socket:socket):
        socket.settimeout(2)
        print(f'listening tcp on {socket.getsockname()}')
        while True:
            try:
                clientSocket, clientAddress = socket.accept()
                client_ip, client_port = clientAddress
                print(f"Accepted connection from {clientAddress}")
                threading.Thread(target=self.listen_user_tcp, args=(clientSocket, clientAddress)).start()
            except:
                if not threading.main_thread().is_alive(): break
        print(f'closing tcp on {socket.getsockname()}')
        # socket.shutdown(SHUT_RDWR)
        # socket.close()

    def listen_user_tcp(self, client_socket:socket, clientAddress):
        client_socket.settimeout(2)
        print(f'listening user tcp on {client_socket.getsockname()}')
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:  
                    print(F'closing socket {client_socket.getsockname()}')
                    client_socket.close()
                    return

                # message = message.decode()

                print(f'{message.decode()} / {client_socket.getsockname()}')
                self.handle(message, clientAddress[1], client_socket)
            except timeout:
                if not threading.main_thread().is_alive(): break
        print(f'closing user tcp on {client_socket.getsockname()}')
        client_socket.shutdown(SHUT_RDWR)
        # client_socket.close()

    def handle(self, message, clientAddr, tcp_socket=None):
        print(f'message: {message}')
        print(f'clientAddress: {clientAddr}')
        HANDLER = {
            'login': self.handle_login,
            # 'logout': handle_logout,
            'pm': self.handle_private_message,
            # 'pmf': handle_private_message_with_file,
            # 'broadcast': handle_broadcast
        }
        data = self.unpack_message(message.decode())
        print(f'data: {data}')
        HANDLER[data[0]](data[1:], clientAddr, tcp_socket)

    def handle_private_message(self, broadcast_data, clientAddr, tcp_socket=None):
        print('handle_private_message, ' + str(broadcast_data))
        print(broadcast_data, clientAddr)
        # sender = USERS_NAMES[clientAddr]['username']
        # receiver = broadcast_data[0]
        message = convert_coma(broadcast_data[1])
        print(message)
        # if (receiver in USERS):
        #     print(f'message: "{message}" to {receiver}')
        #     newMsg = f'[{sender}] {message}'
        #     respond(newMsg, USERS[receiver]['clientAddr'], tcp_socket)
        # else:
        #     print(f'user {receiver} not logged in')
        #     respond(f'user {receiver} not logged in', clientAddr, tcp_socket)

    def handle_login(self, login_data, clientAddr, tcp_socket=None):
        print(f'handling login {login_data}')

    def run(self):
        print('running server')
        threading.Thread(target=self.listen_udp, args=(self.UDP_CONTROLL_SOCKET,)).start()
        threading.Thread(target=self.listen_udp, args=(self.UDP_DATA_SOCKET,)).start()

        threading.Thread(target=self.listen_tcp, args=(self.TCP_CONTROLL_SOCKET,)).start()
        threading.Thread(target=self.listen_tcp, args=(self.TCP_DATA_SOCKET,)).start()

        input()

    def unpack_message(self, message):
        data = message.strip('][').split(', ')
        return data
    
def main():
    server = Server('172.23.64.1', 12000)
    try:
        server.run()
    except KeyboardInterrupt:
        print('bye')
    # except timeout:
    #     print('aaa')

main()