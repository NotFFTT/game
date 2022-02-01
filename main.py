import re
import arcade
import socket
import pickle

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


# SKINS = {
#         '1': ":resources:images/animated_characters/zombie/zombie_idle.png",
#         '2': ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
#         '3': ":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png",
#         '4': ":resources:images/animated_characters/robot/robot_idle.png",
# }

class Game(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.csscolor.BLUE)
        self.player = None
        self.player_number = None
        self.physics_engine = None
        self.skins = None
        self.other_players_list = None

    def setup(self):

        self.skins = {
            '0': arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png"),
            '1': arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"),
            '2': arcade.load_texture(":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png"),
            '3': arcade.load_texture(":resources:images/animated_characters/robot/robot_idle.png"),
        }
        # paths = [":resources:images/animated_characters/zombie/zombie_idle.png", ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", ":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png", ":resources:images/animated_characters/robot/robot_idle.png"]
        # for index, path in enumerate(paths):
        #     self.skins[str(index + 1)] = arcade.load_texture(path)


        self.send('SETUP')
        self.player_number = pickle.loads(client.recv(2048))
        print(self.player_number)
        
        self.player = arcade.Sprite(":resources:images/animated_characters/zombie/zombie_idle.png") # TODO: setting texture then immediately changing it to the new texture is odd. Should just set to the intended texture immediately.
        self.player.texture = self.skins[self.player_number]
        self.player.center_x = 500
        self.player.center_y = 500

        self.other_players_list = arcade.SpriteList()
        
        # self.player2 = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png")
        # self.player2.center_x = 700
        # self.player2.center_y = 500

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
        self.player.draw()
        self.other_players_list.draw()

    def on_update(self, delta_time):
        self.player.update()

        self.send(f"{self.player.center_x} {self.player.center_y} {self.player_number}")
        
        # receive player2 location through socket
        received_list = pickle.loads(client.recv(2048))
        # ['0 0 0', '0 0 0']
        
        # update self.player2.center_x = whatever comes from socket
        print(len(self.other_players_list), len(received_list))
        while len(self.other_players_list) - len(received_list) and len(received_list) - len(self.other_players_list) > 0:
            print("while loop")
            self.other_players_list.append(arcade.Sprite())


        # loop through the other_players_list and update their values to client.recv
        index = 0
        for player in self.other_players_list:
            current = received_list[index].split()
            player.center_x = float(current[0])
            player.center_y = float(current[1])
            player.texture = self.skins[str(current[2])]
            index += 1
        self.other_players_list.update()
        
    def send(self, msg):
        message = pickle.dumps(msg)
        msg_len = len(message)
        send_length = str(msg_len).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

       
def main():
    window = Game()
    window.setup()
    arcade.run()
    

if __name__ == "__main__":
    main()