from ast import Pass
import re
import arcade
import socket
import pickle
import time
import threading
import struct
from pyglet.gl.gl import GL_NEAREST # TODO: Uncomment when ready to add custom tilemap.

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "MULTISHOOTER (please work)"
PLAYER_MOVEMENT_SPEED = 5


PORT = 8080
HEADER = 64
#SERVER = "143.198.247.145"
SERVER = 'localhost'
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
GRAVITY = 1
PLAYER_JUMP_SPEED = 15

HEALTHBAR_WIDTH = 80
HEALTHBAR_HEIGHT = 20
HEALTHBAR_OFFSET_Y = -10
HEALTH_NUMBER_OFFSET_X = -20
HEALTH_NUMBER_OFFSET_Y = -20


# socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

# 2nd UDP socket to receive data from server's multicasted server_data.
server_data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_data_socket.connect((SERVER, 5007))
received_list = ["111 500 0 0 0 0", "110 555 0 0 0 0", "220 500 0 0 0 0", "10 500 0 0 0 0"]
def get_server_data():
    #print('hi')
    while True:
        global received_list
        received_list = pickle.loads(server_data_socket.recv(2048))
        #print('received message: ', received_list)

class Game(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        super().__init__(width, height, title, update_rate=float(1/60))
        arcade.set_background_color(arcade.csscolor.BLUE)
        self.player = None
        self.physics_engine = None
        self.skins = None
        self.other_players_list = None
        self.tile_map = None
        
        self.max_health = None
        self.curr_health = None

        self.time1 = time.time()
        self.time2 = time.time()
        
    def setup(self):

        # TODO: Uncomment when ready to add custom tilemap.
        self.tile_map = arcade.load_tilemap("assets/map1.json", scaling=1.5, use_spatial_hash=True)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.skins = {
            '0': arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png"),
            '1': arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"),
            '2': arcade.load_texture(":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png"),
            '3': arcade.load_texture(":resources:images/animated_characters/robot/robot_idle.png"),
        }

        self.send('SETUP')
        
        self.player = arcade.Sprite() # TODO: does sprite need a texture? # TODO: setting texture then immediately changing it to the new texture is odd. Should just set to the intended texture immediately.
        self.player.player_number = pickle.loads(client.recv(2048))
        self.player.texture = self.skins[self.player.player_number]
        self.player.scale = 0.5
        self.title = f"Player number: {int(self.player.player_number) + 1}"

        self.player.center_x = 100
        self.player.center_y = 160
        
        # TODO: should all sprites be in the scene or not?
        # self.scene.add_sprite_list("Player")
        # self.scene.add_sprite("Player", self.player)

        self.other_players_list = arcade.SpriteList()
        
        # global update_received_list

        # TODO: create a new thread to update_received_list()
        
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, gravity_constant = GRAVITY, walls = self.scene["floor"])

        self.physics_engine.enable_multi_jump(2)


    def on_key_press(self, symbol: int, modifiers: int):

        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.player.change_x = -1 * PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                self.physics_engine.increment_jump_counter()
            # self.player.change_y = PLAYER_MOVEMENT_SPEED
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
            pass
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            pass

    def on_draw(self):
        self.clear()
        self.scene.draw(filter=GL_NEAREST) # TODO: Uncomment when ready to add custom tilemap.
        self.player.draw()

        self.other_players_list.draw()

        player_name = "Player " + str(int(self.player.player_number) + 1)
        arcade.draw_rectangle_filled(
            self.player.center_x,
            self.player.center_y + self.player.height/3,
            width=115,
            height=25,
            color=arcade.color.WHITE,
        )
        arcade.draw_text(
            player_name,
            self.player.center_x - 115/2,
            self.player.center_y + self.player.height/3,
            arcade.color.BLACK,
            font_size = 12,
            bold=True,
            align = "center",
            width=115,
            font_name="Kenney Future",
        )

        # TODO: if there's issues with textbox above player out of alignment with sprite, might need to create textbox off client's version of player instead of server's version.
        for player in self.other_players_list:
            if hasattr(player, "player_number"):
                player_name = "Player " + str(int(player.player_number) + 1)
                arcade.draw_rectangle_filled(
                    player.center_x,
                    player.center_y + player.height/3,
                    width=115,
                    height=25,
                    color=arcade.color.WHITE,
                )
                arcade.draw_text(
                    player_name,
                    player.center_x - 115/2,
                    player.center_y + player.height/3,
                    arcade.color.BLACK,
                    font_size = 12,
                    bold=True,
                    align = "center",
                    width=115,
                    font_name="Kenney Future",
                )

        self.draw_healthbars()

    def draw_healthbars(self):
        self.max_health = 100
        for index, player in enumerate(self.other_players_list):
            
            health_width = HEALTHBAR_WIDTH * (player.curr_health / self.max_health)
            x = (index * SCREEN_WIDTH/5) + SCREEN_WIDTH/5
            
            arcade.draw_rectangle_filled(center_x = x,
                            center_y=40 + HEALTHBAR_OFFSET_Y,
                            width=HEALTHBAR_WIDTH,
                            height=HEALTHBAR_HEIGHT,
                            color=arcade.color.BLACK
            )

            if player.curr_health < self.max_health:
                arcade.draw_rectangle_filled(center_x=x - .5 * (HEALTHBAR_WIDTH - health_width),
                                            center_y=40 + HEALTHBAR_OFFSET_Y,
                                            width=health_width,
                                            height=HEALTHBAR_HEIGHT,
                                            color=arcade.color.GREEN
                )
            
            arcade.draw_text(f"{round(float(player.curr_health/self.max_health) * 100)}%",
                            start_x = x + HEALTH_NUMBER_OFFSET_X,
                            start_y = 40 + HEALTH_NUMBER_OFFSET_Y,
                            font_size=14,
                            color=arcade.color.WHITE
            )
            
            arcade.draw_text(f"PLAYER {index + 1}",
                            start_x = x + HEALTH_NUMBER_OFFSET_X,
                            start_y = 65 + HEALTH_NUMBER_OFFSET_Y,
                            font_size=14,
                            color=arcade.color.WHITE
            )
        
    def send(self, msg):
        message = pickle.dumps(msg)
        # msg_len = len(message)
        # send_length = str(msg_len).encode(FORMAT)
        # send_length += b' ' * (HEADER - len(send_length))
        # client.send(send_length)
        client.send(message)


# AttributeError: ObjCInstance b'NSTrackingArea' has no attribute b'type'

    def on_update(self, delta_time):
        self.player.update()
        self.physics_engine.update()
        
        self.time1 = time.time()
        #print("TIME Loop around>>>>>>>>>", (self.time2 - self.time1))
        #time1
        self.send(f"{self.player.center_x} {self.player.center_y} {self.player.player_number} {time.time_ns()} {self.player.change_x} {self.player.change_y}") # TODO: does send() have a timestamp for server to calculate projected x/y locations that it includes in its published received_list? TODO: necessary to deal with obsolete packets? UDP vs TCP.
        
        # receive player2 location through socket
        #time2
        #received_list = pickle.loads(client.recv(2048)) # TODO: instead of updating received_list in on_update, move it to a separate thread / not even part of Game(arcade.window). TODO: change server to consistently publish received_list on its own interval timer, not trigger by incoming messages. TODO: separate publish channel for chat?
        # ['0 0 0', '0 0 0']
        # print(received_list)
        self.time2 = time.time()
        #print("TIME Between S-R>>>>>>>>>", (self.time2 - self.time1))
        
        # update self.player2.center_x = whatever comes from socket
        #print(len(self.other_players_list), len(received_list))
        while len(received_list) - len(self.other_players_list) and len(received_list) - len(self.other_players_list) > 0:
            #print("while loop")
            self.other_players_list.append(arcade.Sprite())

        # loop through the other_players_list and update their values to client.recv
        index = 0
        # other_players_list = ['0 0 0', '0 0 0', '0 0 0', '0 0 0']
        for player in self.other_players_list:
            current = received_list[index].split()

            server_center_x = float(current[0])
            server_center_y = float(current[1])
            server_change_x = float(current[4])
            server_change_y = float(current[5])
            server_time = int(current[3])
        
            if current[2] == self.player.player_number:
                if self.player.center_y < -1000:
                    # TODO kill player
                    self.player.center_x = 100
                    self.player.center_y = 160
                pass
            player.player_number = str(current[2])

            time_difference = (time.time_ns() - server_time)/1000/1000/1000
            player.center_x = server_center_x + time_difference * 2*server_change_x/delta_time
            player.center_y = server_center_y + time_difference * 2*server_change_y/delta_time - (time_difference/delta_time) ** 2 * GRAVITY
            if arcade.check_for_collision_with_list(player, self.scene["floor"]):
                player.center_y = server_center_y
            #player.change_x = server_change_x
            #player.change_y = server_change_y
            
            player.texture = self.skins[str(current[2])]
            player.curr_health = 80 #TODO update from server
            player.scale = 0.5
            index += 1
    
        self.other_players_list.update()

       
def main():
    thread = threading.Thread(target=get_server_data, args=())
    thread.start()
    window = Game()
    window.setup()
    arcade.run()
    

if __name__ == "__main__":
    main()