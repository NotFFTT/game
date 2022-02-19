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

    # def move_right(self):
    #     if self.player.state != "sp_atk" and self.player.state != 'death':
    #         self.player.change_x = PLAYER_MOVEMENT_SPEED

    def move_left(self):
        if self.player.state != "sp_atk" and self.player.state != 'death':
            self.player.change_x = -1 * PLAYER_MOVEMENT_SPEED

    def jump(self):
        if self.physics_engine.can_jump() and self.player.state != "sp_atk" and self.player.state != 'death':
            self.player.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.male_jump)
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

    def reset_after_death(self):
        if self.player.state == 'death':
            self.player.state = 'idle'
            self.player.curr_health = self.player.max_health
            self.player.center_x = -800
            self.player.center_y = -800

    def on_key_press(self, symbol: int, modifiers: int):
        
        handle_key_press = {
            arcade.key.E: self.player.atk_1, 
            arcade.key.R: self.player.sp_atk,
            arcade.key.RIGHT: self.player.move_right,
            arcade.key.D: self.player.move_right,
            arcade.key.LEFT: self.player.move_left,
            arcade.key.A: self.player.move_left,
            arcade.key.UP: self.jump,
            arcade.key.W: self.jump,
            arcade.key.SPACE: self.jump,
            arcade.key.ESCAPE: self.quit_game,
            arcade.key.F: self.reset_after_death,

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
            player.draw()
        self.player.draw()
        
        # Draw UI
        self.draw_healthbars()
        self.draw_player_labels()
        
    def draw_player_labels(self):

        arcade.draw_rectangle_filled(
            self.player.center_x,
            self.player.center_y + self.player.height/3,
            width=115,
            height=25,
            color=(253, 238, 0, 200),
        )

        arcade.draw_text(
            "Player " + str(self.player.player_number + 1),
            self.player.center_x - 115/2,
            self.player.center_y + self.player.height/3 - 5,
            arcade.color.BLACK,
            font_size = 12,
            bold=True,
            align = "center",
            width=115,
            font_name="Kenney Future",
        )

        for player in self.players_list:
            if player.player_number != self.player.player_number:
                arcade.draw_rectangle_filled(
                    player.center_x,
                    player.center_y + player.height/3,
                    width=115,
                    height=25,
                    color=(255, 255, 255, 100),
                )
                arcade.draw_text(
                    "Player " + str(player.player_number + 1),
                    player.center_x - 115/2,
                    player.center_y + player.height/3 - 5,
                    arcade.color.BLACK,
                    font_size = 12,
                    bold=True,
                    align = "center",
                    width=115,
                    font_name="Kenney Future",
                )

    def draw_healthbars(self):
        self.max_health = 100
        for index, player in enumerate(self.players_list):
            
            health_width = HEALTHBAR_WIDTH * (player.curr_health / self.max_health)
            x = (index * SCREEN_WIDTH/5) + SCREEN_WIDTH/5
            r = 255 * (self.max_health - player.curr_health) / self.max_health
            g = 255 * 2 * player.curr_health / self.max_health if player.curr_health < self.max_health/2 else 255
            b = 20
            
            if player.player_number == self.player.player_number:

                arcade.draw_rectangle_filled(center_x = x,
                                center_y=20+40 + HEALTHBAR_OFFSET_Y,
                                width=HEALTHBAR_WIDTH,
                                height=HEALTHBAR_HEIGHT,
                                color=(r, g, b)
                )

                arcade.draw_text(f"PLAYER {index + 1}",
                                start_x = x + HEALTH_NUMBER_OFFSET_X,
                                start_y = 20+65 + HEALTH_NUMBER_OFFSET_Y,
                                font_size=14,
                                color=arcade.color.WHITE
                )
            
            else:

                arcade.draw_rectangle_filled(center_x = x,
                                center_y=20+40 + HEALTHBAR_OFFSET_Y,
                                width=HEALTHBAR_WIDTH,
                                height=HEALTHBAR_HEIGHT,
                                color=(r, g, b) if abs(player.center_x + 800) > 10 else (200, 200, 200, 155)
                )

                arcade.draw_text(f"PLAYER {index + 1}",
                                start_x = x + HEALTH_NUMBER_OFFSET_X,
                                start_y = 20+65 + HEALTH_NUMBER_OFFSET_Y,
                                font_size=14,
                                color=arcade.color.WHITE if abs(player.center_x + 800) > 10 else (200, 200, 200, 155)
                )

        
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
                server_center_x = float(received_list[index]["x"])
                server_center_y = float(received_list[index]["y"])
                server_change_x = float(received_list[index]["vx"])
                server_change_y = float(received_list[index]["vy"])
                server_state = str(received_list[index]["st"])
                server_character_selection = int(received_list[index]["c"])

                player.player_number = index
                if player.character_selection != server_character_selection:
                    player.character_selection = server_character_selection
                    player.load_character_textures()

                if index == self.player.player_number:
                    if self.player.center_y < -1000:
                        self.player.center_x = 100
                        self.player.center_y = 160
                        player.curr_health = player.max_health
                else:
                    prev_state = player.state
                    player.state = server_state
                    if index == self.player.player_number and player.curr_health == player.max_health:
                        self.player.curr_health = self.player.max_health
                    elif prev_state == 'death' and player.state == 'idle':
                        player.curr_health = player.max_health
                        if index == self.player.player_number:
                            self.player.curr_health = self.player.max_health
                    elif prev_state != player.state and (server_state == 'atk_1' or server_state == 'sp_atk' or server_state == 'death'):
                        player.animation_start = time.time_ns()
                    elif player.state == "death":
                        player.curr_health = 0

                    player.center_x = server_center_x
                    player.center_y = server_center_y

                    player.change_x = server_change_x
                    player.change_y = server_change_y

                    player.set_hit_box(player.texture.hit_box_points)
                
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
