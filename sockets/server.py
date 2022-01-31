from re import M
import socket
import threading

PORT = 9999
HEADER = 64
FORMAT = 'utf-8'
SERVER = 'localhost'
ADDRESS = (SERVER, PORT)

# # # # # # 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDRESS)

player_1_x_y = '700 700 1'
player_2_x_y = '700 700 2'

def handle_client(connection, address, player_name):
    connected = True
    global player_2_x_y
    global player_1_x_y
    
    while connected:
        message_length = connection.recv(HEADER).decode(FORMAT)

        if message_length:
            msg_len = int(message_length)
            msg = connection.recv(msg_len).decode(FORMAT)

            if msg == '!SETUP':
                
                connection.send(str(player_name).encode(FORMAT))
                continue
            
            if player_name == 1:
                player_1_x_y = msg
                connection.send(player_2_x_y.encode(FORMAT))
                print(player_2_x_y)

            else:
                player_2_x_y = msg
                connection.send(player_1_x_y.encode(FORMAT))
                print(player_1_x_y)


    connection.close()

def start():
    server.listen(4)
    print("Waiting for players to connect...")
    
    player_name = 1
    while True:
        connection, address = server.accept()
        # player_texture = SKINS[(player_name) -1]
        # player_name = connection.recv(1024).decode()
        # print(player_name, " has entered the game!", address)

        # connection.send(bytes((player_texture, FORMAT)))
        thread = threading.Thread(target=handle_client, args=(connection, address, player_name))
        player_name += 1
        thread.start()

        print('new connection ', connection)
        
if __name__ == '__main__':
    start()