from ast import Pass
from ctypes.wintypes import CHAR
from locale import currency
import arcade
import socket
import pickle
import time
import threading
from pyglet.gl.gl import GL_NEAREST
import sys
import arcade.gui


# GAME
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "APPLE SMASH!"
GRAVITY = 0.2

# PLAYER
PLAYER_MOVEMENT_SPEED = 2
PLAYER_JUMP_SPEED = 5
HEALTHBAR_WIDTH = 80
HEALTHBAR_HEIGHT = 20
HEALTHBAR_OFFSET_Y = -10
HEALTH_NUMBER_OFFSET_X = -20
HEALTH_NUMBER_OFFSET_Y = -20
CHARACTER_SELECTION = 0

# SERVER
PORT = 8080
PORT2 = 5007
HEADER = 64
SERVER = "143.198.247.145"
#SERVER = 'localhost'
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'

# socket
try:
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sending_socket.connect((SERVER, PORT))
except:
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sending_socket.connect((SERVER, PORT+1))

# 2nd UDP socket to receive data from server's multicasted server_data.
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
            #print(sys.getsizeof(received))
            data = pickle.loads(received)
            if isinstance(data, dict) and set(data.keys()) == {0, 1, 2, 3}:
                received_list = data
                #print(received_list)
            else:
                print("Data not in expected format in get_server_data: ", data)
        except Exception as e:
            print("get_server_data error, received data:", e)
            pass

class Player(arcade.Sprite):
    def __init__(self, player_number=0, max_health=100, character_selection=CHARACTER_SELECTION):
        super().__init__()
        self.max_health = max_health
        self.state = 'idle'
        self.direction = 0
        self.animation_start = time.time_ns()
        self.curr_health = max_health
        self.player_number = player_number
        self.scale = 1
        self.center_x = -800
        self.center_y = -800
        self.character_selection = character_selection
        self.character_type = "fire"
        
        self.sprite_info = {
            "water": {
                "width": 224,
                "height": 112,

                "idle_qty": 8,
                "run_qty": 10,
                "atk_1_qty": 7,
                "sp_atk_qty": 27,
                "jump_qty": 2,
                "death_qty": 16,

                "idle_row": 0,
                "run_row": 1,
                "atk_1_row": 6,
                "sp_atk_row": 8,
                "jump_row": 3,
                "death_row": 13,
            },
            "fire": {
                "width": 224,
                "height": 112,

                "idle_qty": 8,
                "run_qty": 8,
                "atk_1_qty": 11,
                "sp_atk_qty": 18,
                "jump_qty": 2,
                "death_qty": 13,

                "idle_row": 0,
                "run_row": 1,
                "atk_1_row": 6,
                "sp_atk_row": 9,
                "jump_row": 3,
                "death_row": 12,
            },
            "earth": {
                "width": 288,
                "height": 128,

                "idle_qty": 6,
                "run_qty": 8,
                "atk_1_qty": 6,
                "sp_atk_qty": 25,
                "jump_qty": 2,
                "death_qty": 14,

                "idle_row": 0,
                "run_row": 1,
                "atk_1_row": 4,
                "sp_atk_row": 7,
                "jump_row": 3,
                "death_row": 12,
            },
            "wind": {
                "width": 224,
                "height": 112,

                "idle_qty": 8,
                "run_qty": 8,
                "atk_1_qty": 8,
                "sp_atk_qty": 26,
                "jump_qty": 2,
                "death_qty": 12,

                "idle_row": 0,
                "run_row": 1,
                "atk_1_row": 5,
                "sp_atk_row": 7,
                "jump_row": 3,
                "death_row": 11,
            },
        }

        self.animation_cells = None
        self.load_character_textures()

        self.texture = self.animation_cells['idle'][0][self.direction]

    def load_character_textures(self):

        if self.character_selection == 0:
            self.character_type = "fire"
        elif self.character_selection == 1:
            self.character_type = "water"
        elif self.character_selection == 2:
            self.character_type = "wind"
        elif self.character_selection == 3:
            self.character_type = "earth"

        idle = []

        for i in range(self.sprite_info[self.character_type]["idle_qty"]):
            idle.append(self.load_texture_pair_modified(filename=f"assets/{self.character_type}.png", x=i * self.sprite_info[self.character_type]["width"], y=self.sprite_info[self.character_type]["idle_row"] * self.sprite_info[self.character_type]["height"], width=self.sprite_info[self.character_type]["width"], height=self.sprite_info[self.character_type]["height"]))

        run = []
        for i in range(self.sprite_info[self.character_type]["run_qty"]):
            run.append(self.load_texture_pair_modified(filename=f"assets/{self.character_type}.png", x=i * self.sprite_info[self.character_type]["width"], y=self.sprite_info[self.character_type]["run_row"] * self.sprite_info[self.character_type]["height"], width=self.sprite_info[self.character_type]["width"], height=self.sprite_info[self.character_type]["height"]))

        atk_1 = []
        for i in range(self.sprite_info[self.character_type]["atk_1_qty"]):
             atk_1.append(self.load_texture_pair_modified(filename=f"assets/{self.character_type}.png", x=i * self.sprite_info[self.character_type]["width"], y=self.sprite_info[self.character_type]["atk_1_row"] * self.sprite_info[self.character_type]["height"], width=self.sprite_info[self.character_type]["width"], height=self.sprite_info[self.character_type]["height"]))

        sp_atk = []
        for i in range(self.sprite_info[self.character_type]["sp_atk_qty"]):
             sp_atk.append(self.load_texture_pair_modified(filename=f"assets/{self.character_type}.png", x=i * self.sprite_info[self.character_type]["width"], y=self.sprite_info[self.character_type]["sp_atk_row"] * self.sprite_info[self.character_type]["height"], width=self.sprite_info[self.character_type]["width"], height=self.sprite_info[self.character_type]["height"]))

        jump = []
        for i in range(self.sprite_info[self.character_type]["jump_qty"]):
            jump.append(self.load_texture_pair_modified(filename=f"assets/{self.character_type}.png", x=0, y=(self.sprite_info[self.character_type]["jump_row"] + i)*self.sprite_info[self.character_type]["height"], width=self.sprite_info[self.character_type]["width"], height=self.sprite_info[self.character_type]["height"]))

        death = []
        for i in range(self.sprite_info[self.character_type]["death_qty"]):
            death.append(self.load_texture_pair_modified(filename=f"assets/{self.character_type}.png", x=i * self.sprite_info[self.character_type]["width"], y=self.sprite_info[self.character_type]["death_row"] * self.sprite_info[self.character_type]["height"], width=self.sprite_info[self.character_type]["width"], height=self.sprite_info[self.character_type]["height"]))

        self.animation_cells = {
            'idle': idle,
            'run': run,
            'atk_1': atk_1,
            'sp_atk': sp_atk,
            'jump': jump,
            'death': death,
        }

    def load_texture_pair_modified(self, filename, x, y, width, height, hit_box_algorithm: str = "Simple"):
        return [
            arcade.load_texture(filename, x, y, width, height, hit_box_algorithm=hit_box_algorithm),
            arcade.load_texture(filename, x, y, width, height, flipped_horizontally=True, hit_box_algorithm=hit_box_algorithm)
        ]

    def on_update(self, delta_time):
        self.update_animation(delta_time)
        if self.curr_health <= 0 and self.state != 'death':
                self.state = 'death'
                self.animation_start = time.time_ns()
        elif abs(self.change_y) > 0.2 and (self.state != 'atk_1' and self.state != 'sp_atk' and self.state != 'death'):
            self.state = 'jump'
        elif self.change_x > 0:
            if self.state != 'atk_1' and (self.state != 'sp_atk' and self.state != 'death'):
                self.state = 'run'
                self.direction = 0
        elif self.change_x < 0:
            if self.state != 'atk_1' and (self.state != 'sp_atk' and self.state != 'death'):
                self.state = 'run'
                self.direction = 1
        elif self.state != 'atk_1' and self.state != 'sp_atk' and self.state != 'death':
                self.state = 'idle'
        
    def update_animation(self, delta_time):

        if self.state == 'jump':
            if self.change_y > 0:
                self.texture = self.animation_cells[self.state][0][self.direction]
            if self.change_y < 0:
                self.texture = self.animation_cells[self.state][1][self.direction]
            #self.set_hit_box(self.texture.hit_box_points)

        if self.state == 'idle':
            number_of_frames = self.sprite_info[self.character_type]["idle_qty"]
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time) % number_of_frames
            self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
            #self.set_hit_box(self.texture.hit_box_points)

        if self.state == 'run':
            number_of_frames = self.sprite_info[self.character_type]["run_qty"]
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time) % number_of_frames
            self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
            #self.set_hit_box(self.texture.hit_box_points)

        elif self.state == "atk_1":
            number_of_frames = self.sprite_info[self.character_type]["atk_1_qty"]
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time)

            if current_animation_frame + 1 > number_of_frames:
                self.texture = self.animation_cells['idle'][0][self.direction]
                self.set_hit_box(self.texture.hit_box_points)
                self.state = "idle"
            else:
                self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
                self.set_hit_box(self.texture.hit_box_points)

        elif self.state == 'sp_atk':
            number_of_frames = self.sprite_info[self.character_type]["sp_atk_qty"]
            total_animation_time = 1.5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time)

            if current_animation_frame + 1 > number_of_frames:
                self.texture = self.animation_cells['idle'][0][self.direction]
                self.set_hit_box(self.texture.hit_box_points)
                self.state = "idle"
            else:
                self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
                self.set_hit_box(self.texture.hit_box_points)
                
        elif self.state == 'death':
            number_of_frames = self.sprite_info[self.character_type]["death_qty"]
            total_animation_time = 1.5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time)
            if current_animation_frame + 1 > number_of_frames:
                self.texture = self.animation_cells[self.state][number_of_frames - 1][self.direction]
            else:
                self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]


class Game(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        super().__init__(width=width, height=height, title=title)
        arcade.set_background_color(arcade.csscolor.BLUE)

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
        #self.bg_music = arcade.load_sound("assets/sounds/2019-01-22_-_Ready_to_Fight_-_David_Fesliyan.wav")
        
    def setup(self):

        # SETUP SCENE
        self.tile_map = arcade.load_tilemap("assets/map1.json", scaling=1.4, use_spatial_hash=True)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        #arcade.play_sound(self.bg_music, volume=0.5)
        
        # SETUP PLAYER
        self.send('SETUP')
        player_number = pickle.loads(sending_socket.recv(2048))
        self.player = Player(player_number=player_number, character_selection=CHARACTER_SELECTION) 

        # SETUP OTHER PLAYERS
        self.players_list = arcade.SpriteList()
        for i in range(4):
            self.players_list.append(sprite=Player(character_selection=CHARACTER_SELECTION))

        # SETUP PHYSICS
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, gravity_constant = GRAVITY, walls = self.scene["floor"])
        self.physics_engine.enable_multi_jump(2)

    def on_key_press(self, symbol: int, modifiers: int):

        if self.player.state != 'death':

            # DIRECTIONAL
            if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
                if self.player.state != "sp_atk":
                    self.player.change_x = PLAYER_MOVEMENT_SPEED
            elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
                if self.player.state != "sp_atk":
                    self.player.change_x = -1 * PLAYER_MOVEMENT_SPEED
            elif symbol == arcade.key.UP or symbol == arcade.key.W or symbol == arcade.key.SPACE:
                if self.physics_engine.can_jump() and self.player.state != "sp_atk":
                    self.player.change_y = PLAYER_JUMP_SPEED
                    arcade.play_sound(self.male_jump)
                    self.physics_engine.increment_jump_counter()

            # CHARACTER CHANGE
            if symbol == arcade.key.KEY_1 and self.player.state != "sp_atk":
                CHARACTER_SELECTION = 0
                self.player.character_selection = 0
                self.player.load_character_textures()
            elif symbol == arcade.key.KEY_2 and self.player.state != "sp_atk":
                CHARACTER_SELECTION = 1
                self.player.character_selection = 1
                self.player.load_character_textures()
            elif symbol == arcade.key.KEY_3 and self.player.state != "sp_atk":
                CHARACTER_SELECTION = 2
                self.player.character_selection = 2
                self.player.load_character_textures()
            elif symbol == arcade.key.KEY_4 and self.player.state != "sp_atk":
                CHARACTER_SELECTION = 3
                self.player.character_selection = 3
                self.player.load_character_textures()
                    
            # ATTACKS
            elif symbol == arcade.key.E:
                self.player.state = "atk_1"
                arcade.play_sound(self.sword_sound)
                self.player.animation_start = time.time_ns()
            elif symbol == arcade.key.R:
                if self.player.change_y == 0:
                    self.player.state = "sp_atk"
                    arcade.play_sound(self.sword_attack)
                    self.player.animation_start = time.time_ns()
        
        else:
            if symbol == arcade.key.F:
                self.player.state = 'idle'
                self.player.curr_health = self.player.max_health
                self.player.center_x = -800
                self.player.center_y = -800
        
        # QUIT
        if symbol == arcade.key.ESCAPE:
            self.send("DISCONNECT")
            arcade.exit()
            
    def on_key_release(self, symbol: int, modifiers: int):
        
        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.player.change_x = 0
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.player.change_x = 0
        
    def on_draw(self):

        # Draw the scene
        self.clear()
        self.scene.draw(filter=GL_NEAREST)

        # Draw client player
        if not self.player:
            self.setup()
        self.player.draw()
        #self.player.draw_hit_box(color=arcade.color.RED, line_thickness=10)

        # Draw other players
        for player in self.players_list:
            #if player.player_number != self.player.player_number:
            player.draw()
        
        # Draw UI
        self.draw_healthbars()
        self.draw_player_labels()
        
    def draw_player_labels(self):

        arcade.draw_rectangle_filled(
            self.player.center_x,
            self.player.center_y + self.player.height/3,
            width=115,
            height=25,
            color=arcade.color.WHITE,
        )

        arcade.draw_text(
            "Player " + str(self.player.player_number + 1),
            self.player.center_x - 115/2,
            self.player.center_y + self.player.height/3,
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
                    color=arcade.color.WHITE,
                )
                arcade.draw_text(
                    "Player " + str(player.player_number + 1),
                    player.center_x - 115/2,
                    player.center_y + player.height/3,
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
            
            arcade.draw_rectangle_filled(center_x = x,
                            center_y=40 + HEALTHBAR_OFFSET_Y,
                            width=HEALTHBAR_WIDTH,
                            height=HEALTHBAR_HEIGHT,
                            color=arcade.color.BLACK
            )

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
        try:
            message = pickle.dumps(msg)
            sending_socket.send(message)
        except Exception as e:
            print("Error in send method: ", e)

    def on_update(self, delta_time):
        if not self.player:
            self.setup()
        self.player.update()
        self.player.on_update(delta_time)
        self.physics_engine.update()

        # Trigger death animation on current player when equal to or less than zero.
        # if self.player.curr_health <= 0:
        #     self.player.curr_health = 0
        #     self.player.state = 'death'
        #     self.player.animation_start = time.time_ns()
        
        send_data = {
                "x": self.player.center_x,
                "y": self.player.center_y,
                "vx": self.player.change_x,
                "vy": self.player.change_y,
                "dam": self.damage_change,
                "st": self.player.state,
                "c": CHARACTER_SELECTION,
            }

        self.send(send_data)

        # Loop through the other_players_list and update their values to client.recv
        index = 0
        try:
            for player in self.players_list:
                server_center_x = float(received_list[index]["x"])
                server_center_y = float(received_list[index]["y"])
                server_change_x = float(received_list[index]["vx"])
                server_change_y = float(received_list[index]["vy"])
                server_state = str(received_list[index]["st"])
                server_character_selection = str(received_list[index]["c"])

                player.player_number = index
                if player.character_selection != server_character_selection:
                    player.character_selection = server_character_selection
                    player.load_character_textures()
                    print('hi')

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

                index += 1

        except Exception as e:
            print("Error in players list loop: ", e)

        # Decrement health to other players on attack collision. Damage/hit is determined on client side (attacker's side) first.
        self.damage_change = [0,0,0,0]
        if self.player.state == 'atk_1':
            player_hit_list = arcade.check_for_collision_with_list(self.player, self.players_list)
            for player in player_hit_list:
                self.damage_change[player.player_number] = 20*delta_time
        if self.player.state == 'sp_atk':
            player_hit_list = arcade.check_for_collision_with_list(self.player, self.players_list)
            for player in player_hit_list:
                self.damage_change[player.player_number] = 100*delta_time

        self.players_list.update()
        self.players_list.on_update()

# class TitleView(arcade.View):
#     def __init__(self):
#         super().__init__()
#         self.manager = arcade.gui.UIManager()
#         self.manager.enable()
#         self.v_box = arcade.gui.UIBoxLayout()
        
#         start_button = arcade.gui.UIFlatButton(text="Start", width=150)
#         self.v_box.add(start_button.with_space_around(bottom=10))
        
#         @start_button.event('on_click')
#         def on_click_start(event):
#             self.manager.disable()
#             game_view = Game()
#             self.window.show_view(game_view)
#             game_view.setup()
            
#         self.manager.add(
#             arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=self.v_box))
        
#     def on_show(self):
#         arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)
#         arcade.set_viewport(0, self.window.width, 0, self.window.height)

#     def on_draw(self):
#         self.clear()
#         arcade.draw_text("APPLE SMASH", self.window.width/2 , 380, arcade.color.WHITE, font_size=20, anchor_x="center",)
#         self.manager.draw()


# def main():
#     #from title import TitleView
#     thread = threading.Thread(target=get_server_data, args=())
#     thread.start()
#     window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
#     start_view = TitleView()
#     window.show_view(start_view)
#     #start_view.setup()
#     arcade.run()

       
def main():
    thread = threading.Thread(target=get_server_data, args=())
    thread.start()
    window = Game()
    window.setup()
    arcade.run()

    
if __name__ == "__main__":
    main()
