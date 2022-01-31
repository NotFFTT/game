from re import M
import socket
import threading

PORT = 9999
HEADER = 64
FORMAT = 'utf-8'
SERVER = 'localhost'
ADDRESS = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDRESS)


def handle_client(connection, address):
    connected = True

    while connected:
        message_length = connection.recv(HEADER).decode(FORMAT)
        print('Message length: ', message_length)
        if message_length:
            msg_len = int(message_length)
            msg = connection.recv(msg_len).decode(FORMAT)
            print(msg)
    connection.close()

def start():
    server.listen(4)
    print("Waiting for players to connect...")
    
    while True:
        connection, address = server.accept()
        # player_name = connection.recv(1024).decode()
        # print(player_name, " has entered the game!", address)

        # connection.send(bytes(("Welcome to the game! ", FORMAT)))
        
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()

        print('new connection ', connection)
        
if __name__ == '__main__':
    start()