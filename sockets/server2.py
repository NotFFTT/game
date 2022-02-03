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

receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiving_socket.bind(ADDRESS)

players = {
    0: {
        "x": 111,
        "y": 500,
        "vx": 0, # change_x
        "vy": 0, # change_y
        "t": 0, # time
        "dam": [0,0,0,0], # damage
        "st": 0, # state 
    },
    1: {
        "x": 110,
        "y": 555,
        "vx": 0,
        "vy": 0,
        "t": 0,
        "dam": [0,0,0,0],
        "st": 0
    },
    2: {
        "x": 120,
        "y": 555,
        "vx": 0,
        "vy": 0,
        "t": 0,
        "dam": [0,0,0,0],
        "st": 0
    },
    3: { 
        "x": 110,
        "y": 545,
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
    while error_counter < 1:
        if time.time() % 
        print(time.time())
        try:
            msg = pickle.loads(connection.recv(2048))

            if msg == 'SETUP':
                connection.send(pickle.dumps(player_number))
                continue
        
            players[player_number] = msg
            
            if msg == 'DISCONNECT':
                connection.close()
                break

        except Exception as e:
            error_counter += 1
            connection.close()
            print("handle_client error: ", error_counter, e)
            pass

sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sending_socket.bind((SERVER, 5007))
def send_server_data(connection2, address2, player_number):
    error_counter = 0
    while error_counter < 1:
        try:
            time.sleep(random.randint(40, 40) / 1000)
            connection2.sendto(pickle.dumps(players), (SERVER, 5007))
            #print('sent: ', players)
        except Exception as e:
            error_counter += 1
            connection2.close()
            print("send_server_data error: ", error_counter, e)
            pass

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