import arcade
import socket
import pickle
import time
import threading
from pyglet.gl.gl import GL_NEAREST
import sys
import arcade.gui
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    MAP_SELECTION,
    GRAVITY,
    PLAYER_MOVEMENT_SPEED,
    PLAYER_JUMP_SPEED,
    HEALTHBAR_WIDTH,
    HEALTHBAR_HEIGHT,
    HEALTHBAR_OFFSET_Y,
    HEALTH_NUMBER_OFFSET_X,
    HEALTH_NUMBER_OFFSET_Y,
    CHARACTER_SELECTION,
    PORT,
    PORT2,
    HEADER,
    SERVER,
    FORMAT
)
ADDRESS = (SERVER, PORT)
from player import Player

# Set up sending socket.
try:
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sending_socket.connect((SERVER, PORT))
except:
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sending_socket.connect((SERVER, PORT+1))

# Set up receiving socket.
try:
    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    receiving_socket.connect((SERVER, PORT2))
except:
    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    receiving_socket.connect((SERVER, PORT2+1))

received_list = None
def get_server_data():
    global received_list
    while True:
        try:
            received = receiving_socket.recv(2048)

            data = pickle.loads(received)
            if isinstance(data, dict) and set(data.keys()) == {0, 1, 2, 3}:
                received_list = data
            else:
                print("Data not in expected format in get_server_data: ", data)
        except Exception as e:
            print("get_server_data error, received data:", e)
            pass

class Game(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        super().__init__(width=width, height=height, title=title)

        # NEEDED
        self.player = None
        self.physics_engine = None
        self.players_list = None
        self.tile_map = None
        self.damage_change = [0,0,0,0]

        # NOT NEEDED - ONLY FOR DEV
        self.time1 = time.time()
        self.time2 = time.time()

        #LOAD SOUNDS
        self.sword_sound = arcade.load_sound("assets/sounds/sword_slash.wav")
        self.male_jump = arcade.load_sound("assets/sounds/Male_jump.wav")
        self.sword_attack = arcade.load_sound("assets/sounds/sword_swoosh.wav")
        # self.bg_music = arcade.load_sound("assets/sounds/2019-01-22_-_Ready_to_Fight_-_David_Fesliyan.wav")
        
    def setup(self):

        self.setup_scene(MAP_SELECTION)

        self.setup_player(CHARACTER_SELECTION)

        self.setup_remote_players(number_of_players=4)

        self.setup_physics_engine(gravity_const=GRAVITY, walls=self.scene["floor"], max_jumps=2)

    def setup_scene(self, map_path):
        self.tile_map = arcade.load_tilemap(map_path, scaling=1.4, use_spatial_hash=True)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        # arcade.play_sound(self.bg_music, volume=0.5)

    def setup_player(self, character_index):
        self.send_to_server('SETUP')
        player_number = pickle.loads(sending_socket.recv(2048))
        self.player = Player(player_number=player_number, character_selection=character_index) 

    def setup_remote_players(self, number_of_players=4):
        self.players_list = arcade.SpriteList()
        for _ in range(number_of_players):
            self.players_list.append(sprite=Player())

    def setup_physics_engine(self, gravity_const, walls, max_jumps=2):
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, gravity_constant = gravity_const, walls = walls)
        self.physics_engine.enable_multi_jump(max_jumps)

    def make_player_jump(self):
        if self.physics_engine.can_jump():
            self.player.jump()
            self.physics_engine.increment_jump_counter()

    def quit_game(self):
        self.send_to_server("DISCONNECT")
        arcade.exit()

    def change_character(self, character_number):
        if self.player.state != "sp_atk" and self.player.state != 'death':
            CHARACTER_SELECTION = -49 + character_number
            self.player.character_selection = -49 + character_number
            self.player.load_character_textures()
            arcade.play_sound(self.sword_attack)


    def on_key_press(self, symbol: int, modifiers: int):
        
        handle_key_press = {
            arcade.key.E: self.player.atk_1, 
            arcade.key.R: self.player.sp_atk,
            arcade.key.RIGHT: self.player.move_right,
            arcade.key.D: self.player.move_right,
            arcade.key.LEFT: self.player.move_left,
            arcade.key.A: self.player.move_left,
            arcade.key.UP: self.make_player_jump,
            arcade.key.W: self.make_player_jump,
            arcade.key.SPACE: self.make_player_jump,
            arcade.key.ESCAPE: self.quit_game,
            arcade.key.F: self.player.reset_after_death,

        }

        if symbol in [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4]:
            self.change_character(symbol)
        else:
            try:
                handle_key_press.get(symbol)()
            except TypeError:
                print("No action found for that key")


            
    def on_key_release(self, symbol: int, modifiers: int):
        
        if symbol in [arcade.key.RIGHT, arcade.key.D, arcade.key.LEFT, arcade.key.A]:
            self.player.change_x = 0
        
    def on_draw(self):

        # Draw the scene
        self.clear()
        self.scene.draw(filter=GL_NEAREST)

        # Draw client player
        if not self.player:
            self.setup()

        # Draw other players
        for player in self.players_list:
            player.draw_label((255, 255, 255, 100))
            player.draw()
        self.player.draw()
        self.player.draw_label((253, 238, 0, 200))
        
        # Draw UI
        self.draw_healthbars()
    
    @staticmethod
    def player_is_connected(player):
        return player.center_y > -800

    def draw_healthbars(self):

        for player in self.players_list:
            if player.player_number == self.player.player_number:
                self.player.draw_health_bar()
            elif self.player_is_connected(player):
                player.draw_health_bar()
            else:
                player.draw_disconnected()

    def send_to_server(self, msg):
        try:
            message = pickle.dumps(msg)
            sending_socket.send(message)
        except Exception as e:
            print("Error in send method: ", e)

    def update_server(self):
        local_player_data = {
                "x": self.player.center_x,
                "y": self.player.center_y,
                "vx": self.player.change_x,
                "vy": self.player.change_y,
                "dam": self.damage_change,
                "st": self.player.state,
                "c": self.player.character_selection,
            }

        self.send_to_server(local_player_data)

    def update_player_data(self):

        try:
            for index, player in enumerate(self.players_list):

                server_data = {
                'server_center_x': float(received_list[index]["x"]),
                'server_center_y': float(received_list[index]["y"]),
                'server_change_x': float(received_list[index]["vx"]),
                'server_change_y': float(received_list[index]["vy"]),
                'server_state': str(received_list[index]["st"]),
                'server_character_selection': int(received_list[index]["c"]),
                'prev_state': player.state,
                'player_number': index,
                }


                player.player_number = index
                if index == self.player.player_number:
                    self.player.local_update_with_server_data(server_data)
                else:
                    player.update_with_server_data(server_data)
                
                # Update damage to all players including client based on damage in recieved_data from server.
                for key, value in received_list.items():
                    if index == self.player.player_number:
                        self.player.curr_health -= value["dam"][index]
                        self.player.curr_health = 0 if self.player.state == 'death' else self.player.curr_health
                    player.curr_health -= value["dam"][index]
                    player.curr_health = 0 if player.curr_health <= 0 else player.curr_health

        except Exception as e:
            print("Error in players list loop: ", e)

    def update_damage_inflicted(self, delta_time):
        # Decrement health to other players on attack collision. Damage/hit is determined on client side (attacker's side) first.
        attack_damage = {'atk_1': 20 * delta_time, 'sp_atk': 100 * delta_time}  
        self.damage_change = [0,0,0,0]

        player_hit_list = arcade.check_for_collision_with_list(self.player, self.players_list) 
        
        for player in player_hit_list:
            self.damage_change[player.player_number] = attack_damage.get(self.player.state)

    def on_update(self, delta_time):
        if not self.player:
            self.setup()
        self.player.update()
        self.player.on_update(delta_time)
        self.physics_engine.update()

        self.update_server()

        self.update_player_data()

        if self.player.state == 'atk_1' or self.player.state == 'sp_atk':
            self.update_damage_inflicted(delta_time)
        else:
            self.damage_change = [0,0,0,0]

        self.players_list.update()
        self.players_list.on_update()

       
def main():
    thread = threading.Thread(target=get_server_data, args=())
    thread.start()
    window = Game()
    window.setup()
    arcade.run()

    
if __name__ == "__main__":
    main()
