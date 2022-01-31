import arcade
import socket

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "MULTISHOOTER (please work)"
PLAYER_MOVEMENT_SPEED = 3
PORT = 9999
HEADER = 64
SERVER = 'localhost'
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)
# player_name = input("Enter your name > ")

# print(client.recv(1024).decode())

class Game(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.csscolor.BLUE)
        self.player = None
        
        self.physics_engine = None

    def setup(self):
        self.player = arcade.Sprite(":resources:images/animated_characters/zombie/zombie_idle.png")
        self.player.center_x = 500
        self.player.center_y = 500
        
        self.player2 = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png")
        self.player2.center_x = 700
        self.player2.center_y = 500

    def on_key_press(self, symbol: int, modifiers: int):

        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.player.change_x = -1 * PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            self.player.change_y = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.player.change_y = -1 * PLAYER_MOVEMENT_SPEED
            
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
        self.player2.draw()

    def on_update(self, delta_time):
        self.player.update()

        self.send(f"{self.player.center_x} {self.player.center_y}")

        # receive player2 location through socket
        received_list = client.recv(2048).decode(FORMAT)
        print(received_list)
        received_list = received_list.split(" ")
        
        # update self.player2.center_x = whatever comes from socket
        self.player2.center_x = float(received_list[0])
        self.player2.center_y = float(received_list[1])
        self.player2.update()
        
    def send(self, msg):
        message = msg.encode(FORMAT)
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