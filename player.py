import arcade
import time
from constants import PLAYER_MOVEMENT_SPEED, PLAYER_JUMP_SPEED
class Player(arcade.Sprite):
    def __init__(self, player_number=0, max_health=100, character_selection=0):
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
        self.sword_sound = arcade.load_sound("assets/sounds/sword_slash.wav")
        self.male_jump = arcade.load_sound("assets/sounds/Male_jump.wav")
        self.sword_attack = arcade.load_sound("assets/sounds/sword_swoosh.wav")
        
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

    def draw_label(self, bg_color):
        arcade.draw_rectangle_filled(
            self.center_x,
            self.center_y + self.height/3,
            width=115,
            height=25,
            color=bg_color,
        )

        arcade.draw_text(
            "Player " + str(self.player_number + 1),
            self.center_x - 115/2,
            self.center_y + self.height/3 - 5,
            arcade.color.BLACK,
            font_size = 12,
            bold=True,
            align = "center",
            width=115,
            font_name="Kenney Future",
        )
    
    def atk_1(self):
        if self.state != 'death':
            self.state = "atk_1"
            arcade.play_sound(self.sword_sound)
            self.animation_start = time.time_ns()

    def sp_atk(self):
        if abs(self.change_y) <= 0.5 and self.state != 'death': 
            self.state = "sp_atk"
            arcade.play_sound(self.sword_attack)
            self.animation_start = time.time_ns()
    
    def move_right(self):
        if self.state != "sp_atk" and self.state != 'death':
            self.change_x = PLAYER_MOVEMENT_SPEED

    def move_left(self):
        if self.state != "sp_atk" and self.state != 'death':
            self.change_x = -1 * PLAYER_MOVEMENT_SPEED

    def jump(self):
        if self.state != "sp_atk" and self.state != 'death':
            self.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.male_jump)

    def reset_after_death(self):
        if self.state == 'death':
            self.state = 'idle'
            self.curr_health = self.max_health
            self.center_x = -800
            self.center_y = -800


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

