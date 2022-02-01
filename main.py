import re
import arcade
import socket
import pickle
import time
import threading
from pyglet.gl.gl import GL_NEAREST # TODO: Uncomment when ready to add custom tilemap.

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "MULTISHOOTER (please work)"
PLAYER_MOVEMENT_SPEED = 13
PORT = 8080
HEADER = 64

# SERVER = "143.198.247.145"
SERVER = 'localhost'
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'

# socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

# thread = threading.Thread(target=update_received_list, args=())
# thread.start()

# received_list = None
# def update_received_list():
#     while True:
#         global received_list
#         received_list = pickle.loads(client.recv(2048))

class Game(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.csscolor.BLUE)
        self.player = None
        self.player_number = None
        self.physics_engine = None
        self.skins = None
        self.other_players_list = None
        self.tile_map = None

        self.time1 = time.time()
        self.time2 = time.time()

    def setup(self):

        # TODO: Uncomment when ready to add custom tilemap.
        self.tile_map = arcade.load_tilemap("assets/map1.json", scaling=2, use_spatial_hash=True)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.skins = {
            '0': arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png"),
            '1': arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"),
            '2': arcade.load_texture(":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png"),
            '3': arcade.load_texture(":resources:images/animated_characters/robot/robot_idle.png"),
        }

        self.send('SETUP')
        self.player_number = pickle.loads(client.recv(2048))
        self.title = f"Player number: {int(self.player_number) + 1}"
        
        self.player = arcade.Sprite() # TODO: does sprite need a texture? # TODO: setting texture then immediately changing it to the new texture is odd. Should just set to the intended texture immediately.
        self.player.texture = self.skins[self.player_number]
        self.player.center_x = 500
        self.player.center_y = 500

        self.other_players_list = arcade.SpriteList()
        
        # global update_received_list

        # TODO: create a new thread to update_received_list()
    

    def on_key_press(self, symbol: int, modifiers: int):

        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.player.change_x = -1 * PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            self.player.change_y = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.player.change_y = -1 * PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.Q:
            self.send("DISCONNECT")
            arcade.exit()
            
    def on_key_release(self, symbol: int, modifiers: int):
        
        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.player.change_x = 0
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.player.change_x = 0
        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            self.player.change_y = 0
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.player.change_y = 0

    def on_draw(self):
        self.clear()
        self.scene.draw(filter=GL_NEAREST) # TODO: Uncomment when ready to add custom tilemap.
        self.player.draw()
        self.other_players_list.draw()

        

        # arcade.draw_text(
        #     player_name,
        #     self.player.center_x - self.player.height/4,
        #     self.player.center_y + self.player.height/3,
        #     arcade.color.WHITE,
        #     font_size = 12,
        #     align = "center",
        #     width=90,
        # )

        for player in self.other_players_list:
            player_name = "Player " + str(int(player.name) + 1)
            arcade.draw_text(
                player_name,
                player.center_x - player.height/4,
                player.center_y + player.height/3,
                arcade.color.WHITE,
                font_size = 12,
                align = "center",
                width=90,
            )

    def send(self, msg):
        message = pickle.dumps(msg)
        msg_len = len(message)
        send_length = str(msg_len).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

    def on_update(self, delta_time):
        self.player.update()

        self.time1 = time.time()
        # print("TIME Loop around>>>>>>>>>", (self.time2 - self.time1))
        #time1
        self.send(f"{self.player.center_x} {self.player.center_y} {self.player_number}") # TODO: does send() have a timestamp for server to calculate projected x/y locations that it includes in its published received_list? TODO: necessary to deal with obsolete packets? UDP vs TCP.
        
        # receive player2 location through socket
        #time2
        received_list = pickle.loads(client.recv(2048)) # TODO: instead of updating received_list in on_update, move it to a separate thread / not even part of Game(arcade.window). TODO: change server to consistently publish received_list on its own interval timer, not trigger by incoming messages. TODO: separate publish channel for chat?
        # ['0 0 0', '0 0 0']
        print(received_list)
        self.time2 = time.time()
        # print("TIME Between S-R>>>>>>>>>", (self.time2 - self.time1))
        
        # update self.player2.center_x = whatever comes from socket
        # print(len(self.other_players_list), len(received_list))
        while len(self.other_players_list) - len(received_list) and len(received_list) - len(self.other_players_list) > 0:
            print("while loop")
            self.other_players_list.append(arcade.Sprite())

        # loop through the other_players_list and update their values to client.recv
        index = 0
        # other_players_list = ['0 0 0', '0 0 0', '0 0 0', '0 0 0']
        for player in self.other_players_list:
            current = received_list[index].split()
            player.name = str(current[2])
            player.center_x = float(current[0])
            player.center_y = float(current[1])
            player.texture = self.skins[str(current[2])]
            index += 1
    
        self.other_players_list.update()

       
def main():
    window = Game()
    window.setup()
    arcade.run()
    

if __name__ == "__main__":
    main()