from ast import Pass
from locale import currency
import arcade
import socket
import pickle
import time
import threading
from pyglet.gl.gl import GL_NEAREST
import sys

# GAME
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "MULTISHOOTER (please work)"
GRAVITY = 0.2

# PLAYER
PLAYER_MOVEMENT_SPEED = 2
PLAYER_JUMP_SPEED = 5
HEALTHBAR_WIDTH = 80
HEALTHBAR_HEIGHT = 20
HEALTHBAR_OFFSET_Y = -10
HEALTH_NUMBER_OFFSET_X = -20
HEALTH_NUMBER_OFFSET_Y = -20

# SERVER
PORT = 8080
HEADER = 64
SERVER = "143.198.247.145"
# SERVER = 'localhost'
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'

# socket
sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sending_socket.connect(ADDRESS)

# 2nd UDP socket to receive data from server's multicasted server_data.
receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
receiving_socket.connect((SERVER, 5007))
received_list = {
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
def get_server_data():
    while True:
        global received_list
        try:
            received = receiving_socket.recv(2048)
            print(sys.getsizeof(received))
            data = pickle.loads(received)
            if isinstance(data, dict) and set(data.keys()) == {0, 1, 2, 3}:
                received_list = data
            else:
                print("Data not in expected format in get_server_data: ", data)
        except Exception as e:
            print("get_server_data error, received data:", e)
            pass


class Player(arcade.Sprite):
    def __init__(self, player_number=0, max_health=100):
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


        # if self.player_number == 0:
        #     self.element = "fire"
        # elif self.player_number == 1:
        #     self.element = "earth"
        # elif self.player_number == 2:
        #     self.element = "water"
        # elif self.player_number == 3:
        #     self.element = "wizard"

        # idle = []
        # for i in range(6):
        #     idle.append(arcade.load_texture_pair(f"assets/earth/idle/idle_{i+1}.png"))

        # run = []
        # for i in range(8):
        #     run.append(arcade.load_texture_pair(f"assets/earth/run/run_{i+1}.png"))
            
        # atk_1 = []
        # for i in range(6):
        #      atk_1.append(arcade.load_texture_pair(f"assets/earth/1_atk/1_atk_{i+1}.png"))
        
        # sp_atk = []
        # for i in range(25):
        #      sp_atk.append(arcade.load_texture_pair(f"assets/earth/sp_atk/sp_atk_{i+1}.png"))

        idle = []
        for i in range(8):
            idle.append(arcade.load_texture_pair(f"assets/fire/idle/idle_{i+1}.png"))

        run = []
        for i in range(8):
            run.append(arcade.load_texture_pair(f"assets/fire/run/run_{i+1}.png"))
            
        atk_1 = []
        for i in range(11):
             atk_1.append(arcade.load_texture_pair(f"assets/fire/05_1_atk/1_atk_{i+1}.png"))
        
        sp_atk = []
        for i in range(28):
             sp_atk.append(arcade.load_texture_pair(f"assets/fire/07_3_atk/3_atk_{i+1}.png"))

        jump = []
        for i in range(20):
            jump.append(arcade.load_texture_pair(f"assets/fire/jump/jump_{i+1}.png"))
            
        death = []
        for i in range(13):
            death.append(arcade.load_texture_pair(f"assets/fire/11_death/death_{i+1}.png"))

        self.animation_cells = {
            'idle': idle,
            'run': run,
            'atk_1': atk_1,
            'sp_atk': sp_atk,
            'jump': jump,
            'death': death,
        }

        self.texture = self.animation_cells['idle'][0][self.direction]

    def on_update(self, delta_time):
        self.update_animation(delta_time)
        if self.curr_health <= 0:
                self.state = 'death'
                self.animation_start = time.time_ns()
        elif abs(self.change_y) > 0.2 and (self.state != 'atk_1' and self.state != 'sp_atk'):
            self.state = 'jump'
        elif self.change_x > 0:
            if self.state != 'atk_1' and self.state != 'sp_atk':
                self.state = 'run'
                self.direction = 0
        elif self.change_x < 0:
            if self.state != 'atk_1' and self.state != 'sp_atk':
                self.state = 'run'
                self.direction = 1
        elif self.state != 'atk_1' and self.state != 'sp_atk':
                self.state = 'idle'
        
            

    def update_animation(self, delta_time):

        if self.state == 'jump':
            if self.change_y > 0:
                self.texture = self.animation_cells[self.state][5][self.direction]
            if self.change_y < 0:
                self.texture = self.animation_cells[self.state][15][self.direction]
            #self.set_hit_box(self.texture.hit_box_points)

        if self.state == 'idle':
            number_of_frames = 8
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time) % number_of_frames
            self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
            #self.set_hit_box(self.texture.hit_box_points)

        if self.state == 'run':
            number_of_frames = 8
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time) % number_of_frames
            self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
            #self.set_hit_box(self.texture.hit_box_points)

        elif self.state == "atk_1":
            number_of_frames = 11
            total_animation_time = .5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time)

            if current_animation_frame + 1 > number_of_frames:
                self.state = "idle"
            else:
                self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
                self.set_hit_box(self.texture.hit_box_points)

        elif self.state == 'sp_atk':
            number_of_frames = 28
            total_animation_time = 1.5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000 # time_diff is in units of seconds
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time)

            if current_animation_frame + 1 > number_of_frames:
                self.state = "idle"
            else:
                self.texture = self.animation_cells[self.state][current_animation_frame][self.direction]
                self.set_hit_box(self.texture.hit_box_points)
                
        elif self.state == 'death':
            number_of_frames = 13
            total_animation_time = 1.5
            time_now = time.time_ns()
            time_diff = (time_now - self.animation_start) / 1000 / 1000 / 1000
            current_animation_frame = round(time_diff * number_of_frames / total_animation_time)

class Game(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):

        super().__init__(width, height, title, update_rate=float(1/60))
        arcade.set_background_color(arcade.csscolor.BLUE)

        # NEEDED
        self.player = None
        self.physics_engine = None
        self.other_players_list = None
        self.tile_map = None
        self.damage_change = [0,0,0,0]

        # NOT NEEDED - ONLY FOR DEV
        self.time1 = time.time()
        self.time2 = time.time()

        #LOAD SOUNDS
        self.sword_sound = arcade.load_sound("assets/sounds/sword_slash.wav")
        self.male_jump = arcade.load_sound("assets/sounds/Male_jump.wav")
        self.sword_attack = arcade.load_sound("assets/sounds/sword_swoosh.wav")
        
        
    def setup(self):

        # SETUP SCENE
        self.tile_map = arcade.load_tilemap("assets/map1.json", scaling=1.4, use_spatial_hash=True)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # SETUP PLAYER
        self.send('SETUP')
        player_number = pickle.loads(sending_socket.recv(2048))
        self.player = Player(player_number=player_number) 

        # SETUP OTHER PLAYERS
        self.other_players_list = arcade.SpriteList()
        for i in range(4):
            self.other_players_list.append(sprite=Player())

        # SETUP PHYSICS
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, gravity_constant = GRAVITY, walls = self.scene["floor"])
        self.physics_engine.enable_multi_jump(2)

    def on_key_press(self, symbol: int, modifiers: int):

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
        
        # QUIT
        elif symbol == arcade.key.Q:
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
        self.player.draw()
        #self.player.draw_hit_box(color=arcade.color.RED, line_thickness=10)

        # Draw other players
        for player in self.other_players_list:
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

        for player in self.other_players_list:
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
        for index, player in enumerate(self.other_players_list):
            
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
        message = pickle.dumps(msg)
        sending_socket.send(message)

    def on_update(self, delta_time):
        self.player.update()
        self.player.on_update(delta_time)
        self.physics_engine.update()
        
        send_data = {
                "x": self.player.center_x,
                "y": self.player.center_y,
                "vx": self.player.change_x, # change_x
                "vy": self.player.change_y, # change_y
                "t": time.time_ns(), # time
                "dam": self.damage_change, # damage
                "st": self.player.state, # state 
            }

        self.send(send_data)

        # Loop through the other_players_list and update their values to client.recv
        index = 0

        for player in self.other_players_list:
            
            server_center_x = float(received_list[index]["x"])
            server_center_y = float(received_list[index]["y"])
            server_change_x = float(received_list[index]["vx"])
            server_change_y = float(received_list[index]["vy"])
            server_time = int(received_list[index]["t"])
            server_state = str(received_list[index]["st"])

            player.player_number = index
        
            if index == self.player.player_number:
                if self.player.center_y < -1000:
                    # TODO kill player
                    self.player.center_x = 100
                    self.player.center_y = 160
            else:
                prev_state = player.state
                player.state = server_state
                if prev_state != player.state and (server_state == 'atk_1' or server_state == 'sp_atk'):
                    player.animation_start = time.time_ns()

                time_difference = (time.time_ns() - server_time)/1000/1000/1000

                player.center_x = server_center_x# + time_difference * 2*server_change_x/delta_time # TODO: This prediction depends on client's clocks being synced and consistent epoch. 
                if player.texture and arcade.check_for_collision_with_list(player, self.scene["floor"]):
                    player.center_x = server_center_x

                player.center_y = server_center_y# + time_difference * 2*server_change_y/delta_time - (time_difference/delta_time) ** 2 * GRAVITY
                if player.texture and arcade.check_for_collision_with_list(player, self.scene["floor"]):
                    player.center_y = server_center_y

                player.change_x = server_change_x
                player.change_y = server_change_y

                player.set_hit_box(player.texture.hit_box_points)
            
            # Update damage to all players including client based on damage in recieved_data from server.
            for key, value in received_list.items():
                if index == self.player.player_number:
                    self.player.curr_health -= value["dam"][index]
                player.curr_health -= value["dam"][index]

            index += 1

        # Decrement Health On Attack Collision
        self.damage_change = [0,0,0,0]
        if self.player.state == 'atk_1':
            player_hit_list = arcade.check_for_collision_with_list(self.player, self.other_players_list)

            for player in player_hit_list:
                #player.curr_health -= 5*delta_time
                self.damage_change[player.player_number] = 5*delta_time
                if player.curr_health < 0:
                    player.curr_health = 0
                    continue # TODO: kill player

        self.other_players_list.update()
        self.other_players_list.on_update()

       
def main():
    thread = threading.Thread(target=get_server_data, args=())
    thread.start()
    window = Game()
    window.setup()
    arcade.run()
    

if __name__ == "__main__":
    main()