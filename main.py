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

            data = pickle.loads(received)
            if isinstance(data, dict) and set(data.keys()) == {0, 1, 2, 3}:
                received_list = data
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
                "death_qty": 19,

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

        self.texture = self.animation_cells['idle'][0][self.direction]

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
                self.direction = 0
                if self.state != 'run' and self.state != 'jump':
                    self.texture = self.animation_cells['run'][0][self.direction]
                    self.set_hit_box(self.texture.hit_box_points)
                self.state = 'run'
        elif self.change_x < 0:
            if self.state != 'atk_1' and (self.state != 'sp_atk' and self.state != 'death'):
                self.direction = 1
                if self.state != 'run' and self.state != 'jump':
                    self.texture = self.animation_cells['run'][0][self.direction]
                    self.set_hit_box(self.texture.hit_box_points)
                self.state = 'run'
        elif self.state != 'atk_1' and self.state != 'sp_atk' and self.state != 'death':
                self.state = 'idle'
        
    def update_animation(self, delta_time):

        if self.state == 'jump':
            if self.change_y > 0:
                self.texture = self.animation_cells[self.state][0][self.direction]
            if self.change_y < 0:
                self.texture = self.animation_cells[self.state][1][self.direction]


        if self.state == 'idle':
            number_of_frames = self.sprite_info[self.character_type]["idle_qty"]
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time) % number_of_frames
            self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]


        if self.state == 'run':
            number_of_frames = self.sprite_info[self.character_type]["run_qty"]
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time) % number_of_frames
            self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]


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

        self.setup_scene()

        self.setup_player()

        self.setup_remote_players()

        # SETUP PHYSICS
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, gravity_constant = GRAVITY, walls = self.scene["floor"])
        self.physics_engine.enable_multi_jump(2)

    def setup_scene(self):
        self.tile_map = arcade.load_tilemap(MAP_SELECTION, scaling=1.4, use_spatial_hash=True)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        #arcade.play_sound(self.bg_music, volume=0.5)

    def setup_player(self):
        self.send_to_server('SETUP')
        player_number = pickle.loads(sending_socket.recv(2048))
        self.player = Player(player_number=player_number, character_selection=CHARACTER_SELECTION) 

    def setup_remote_players(self):
        self.players_list = arcade.SpriteList()
        for _ in range(4):
            self.players_list.append(sprite=Player(character_selection='CHARACTER_SELECTION'))

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
                arcade.play_sound(self.sword_attack)
            elif symbol == arcade.key.KEY_2 and self.player.state != "sp_atk":
                CHARACTER_SELECTION = 1
                self.player.character_selection = 1
                self.player.load_character_textures()
                arcade.play_sound(self.sword_attack)
            elif symbol == arcade.key.KEY_3 and self.player.state != "sp_atk":
                CHARACTER_SELECTION = 2
                self.player.character_selection = 2
                self.player.load_character_textures()
                arcade.play_sound(self.sword_attack)
            elif symbol == arcade.key.KEY_4 and self.player.state != "sp_atk":
                CHARACTER_SELECTION = 3
                self.player.character_selection = 3
                self.player.load_character_textures()
                arcade.play_sound(self.sword_attack)
                    
            # ATTACKS
            elif symbol == arcade.key.E:
                self.player.state = "atk_1"
                arcade.play_sound(self.sword_sound)
                self.player.animation_start = time.time_ns()
            elif symbol == arcade.key.R:
                if abs(self.player.change_y) <= 0.5: 
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
            self.send_to_server("DISCONNECT")
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
