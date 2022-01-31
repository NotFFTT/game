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

player_1_x_y = None
player_2_x_y = None

def handle_client(connection, address, player_name):
    connected = True
    
    while connected:
        message_length = connection.recv(HEADER).decode(FORMAT)
        print('Message length: ', message_length)
        if message_length:
            msg_len = int(message_length)
            msg = connection.recv(msg_len).decode(FORMAT)
            
            if player_name == 1:
                player_1_x_y = msg
                print('PLAYER ONE', player_1_x_y)

            else:
                player_2_x_y = msg
                print('PLAYER TWO', player_2_x_y)

    connection.close()

def start():
    server.listen(4)
    print("Waiting for players to connect...")
    
    player_name = 1
    while True:
        connection, address = server.accept()
        # player_name = connection.recv(1024).decode()
        # print(player_name, " has entered the game!", address)

        # connection.send(bytes(("Welcome to the game! ", FORMAT)))
        
        thread = threading.Thread(target=handle_client, args=(connection, address, player_name))
        player_name += 1
        thread.start()

        print('new connection ', connection)
        
if __name__ == '__main__':
    start()