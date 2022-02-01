from re import M
import socket
import threading
import pickle

#PORT = 9999
PORT = 8080
HEADER = 64
FORMAT = 'utf-8'
SERVER = 'localhost'
# SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)

# # # # # # 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDRESS)

players = ["0 0 0", "0 0 0", "0 0 0", "0 0 0"]

def handle_client(connection, address, player_number):
    connected = True
    global players
    
    while connected:
        message_length = connection.recv(HEADER).decode(FORMAT)

        if message_length:
            msg_len = int(message_length)
            msg = pickle.loads(connection.recv(msg_len))

            if msg == 'SETUP':
                #ADD NEW PLAYER
                players[player_number] = "0 0 0"
                connection.send(pickle.dumps(str(player_number)))
                continue
        
            players[player_number] = msg
            
            if msg == 'DISCONNECT':
                #REMOVE PLAYER
                del players[player_number]
                connection.close()
                break

            #UPDATE PLAYER DATA
            connection.send(pickle.dumps(players))

    connection.close()

def start():
    server.listen(4)
    print("Waiting for players to connect...")
    
    player_number = 0
    while True:
        connection, address = server.accept()

        thread = threading.Thread(target=handle_client, args=(connection, address, player_number))
        player_number = (player_number + 1) % 4
        thread.start()

        print('new connection ', connection)
        
if __name__ == '__main__':
    start()