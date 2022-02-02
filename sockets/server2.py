from re import M
import socket
import threading
import pickle
import time
import random

#PORT = 9999
PORT = 8080
HEADER = 64
FORMAT = 'utf-8'
#SERVER = 'localhost'
SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

players = ["111 500 0 0 0 0", "110 555 0 0 0 0", "220 500 0 0 0 0", "10 500 0 0 0 0"]
def handle_client(connection, address, player_number):
    connected = True
    global players
    
    while connected:
        #message_length = connection.recv(HEADER).decode(FORMAT)

        #if message_length:
        #msg_len = int(message_length)
        msg = pickle.loads(connection.recv(2048))

        if msg == 'SETUP':
            #ADD NEW PLAYER
            #players[player_number] = "0 0 0"
            players[player_number] = f"{player_number * 100} 500 0 0 0 0"
            connection.send(pickle.dumps(str(player_number)))   # TODO: do not send back data when setup if global received_list is used.
            continue
    
        players[player_number] = msg
        
        if msg == 'DISCONNECT':
            #REMOVE PLAYER
            #del players[player_number] # TODO: Uncomment when list actually works as a variable length list
            players[player_number] = "550 550 0 0 0 0"
            connection.close()
            break

            #UPDATE PLAYER DATA
            #connection.send(pickle.dumps(players))

# https://stackoverflow.com/questions/603852/how-do-you-udp-multicast-in-python
server_data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_data_socket.bind((SERVER, 5007))
def send_server_data(connection2, address2, player_number):
    try:
        while True:
            time.sleep(random.randint(20, 20) / 1000)
            connection2.sendto(pickle.dumps(players), (SERVER, 5007))
            #print('sent: ', players)
    except:
        print('BrokenPipeError') # TODO: Make an actual exception.

def start():
    server.listen(4)
    server_data_socket.listen(4)
    print("Waiting for players to connect...")

    player_number = 0
    while True:
        connection, address = server.accept()
        connection2, address2 = server_data_socket.accept()

        thread = threading.Thread(target=send_server_data, args=(connection2, address2, player_number))
        thread.start()

        thread = threading.Thread(target=handle_client, args=(connection, address, player_number))
        player_number = (player_number + 1) % 4
        thread.start()

        print('new connection ', connection)
        
if __name__ == '__main__':
    start()