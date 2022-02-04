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
SERVER = 'localhost'
# SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)

receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
receiving_socket.bind(ADDRESS)

players = {
    0: {
        "x": -800,
        "y": -800,
        "vx": 0, # change_x
        "vy": 0, # change_y
        "t": 0, # time
        "dam": [0,0,0,0], # damage
        "st": 0, # state 
    },
    1: {
        "x": -800,
        "y": -800,
        "vx": 0,
        "vy": 0,
        "t": 0,
        "dam": [0,0,0,0],
        "st": 0
    },
    2: {
        "x": -800,
        "y": -800,
        "vx": 0,
        "vy": 0,
        "t": 0,
        "dam": [0,0,0,0],
        "st": 0
    },
    3: { 
        "x": -800,
        "y": -800,
        "vx": 0,
        "vy": 0,
        "t": 0,
        "dam": [0,0,0,0],
        "st": 0,
    },
}

def handle_client(connection, address, player_number):
    connected = True
    global players
    
    error_counter = 0
    max_error_count = 5
    while error_counter <= max_error_count:
        try:
            msg = pickle.loads(connection.recv(2048))

            if msg == 'SETUP':
                connection.send(pickle.dumps(player_number))
                continue
        
            players[player_number] = msg
            
            if msg == 'DISCONNECT':
                connection.close()
                break

            error_counter -= 1
            if error_counter < 0:
                error_counter = 0

        except Exception as e:
            error_counter += 1
            if error_counter > max_error_count:
                connection.close()
            print("handle_client error: ", error_counter, e)
            pass
    if error_counter > max_error_count:
        connection.close()

sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sending_socket.bind((SERVER, 5007))
def send_server_data(connection2, address2, player_number):
    error_counter = 0
    max_error_count = 5
    while error_counter <= 5:
        try:
            time.sleep(random.randint(40, 40) / 1000)
            connection2.sendto(pickle.dumps(players), (SERVER, 5007))
            error_counter -= 1
            if error_counter < 0:
                error_counter = 0
        except Exception as e:
            error_counter += 1
            if error_counter > max_error_count:
                connection2.close()
            print("send_server_data error: ", error_counter, e)
            pass
    if error_counter > max_error_count:
        connection2.close()

def start():
    receiving_socket.listen(4)
    sending_socket.listen(4)
    print("Waiting for players to connect...")

    player_number = 0
    while True:
        connection, address = receiving_socket.accept()
        connection2, address2 = sending_socket.accept()

        thread = threading.Thread(target=send_server_data, args=(connection2, address2, player_number))
        thread.start()

        thread = threading.Thread(target=handle_client, args=(connection, address, player_number))
        player_number = (player_number + 1) % 4
        thread.start()

        print('new connection ', connection)
        
if __name__ == '__main__':
    start()