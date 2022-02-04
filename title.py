from tracemalloc import start
import arcade
import arcade.gui

WIDTH = 1000
HEIGHT = 650

class TitleView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box2 = arcade.gui.UIBoxLayout()
        self.v_box = arcade.gui.UIBoxLayout(vertical=False )
        self.background = None
        
        
        
        start_button = arcade.gui.UIFlatButton(text="Start" )
        self.v_box2.add(start_button.with_space_around(bottom=10))
        
        play_1_img = arcade.gui.UITextureButton(x=0, y=0, texture=arcade.load_texture('assets/fire/idle/idle_1.png'))
        self.v_box.add(play_1_img.with_space_around(bottom=10))
        
        play_2_img = arcade.gui.UITextureButton(x=0, y=0, texture=arcade.load_texture('assets/earth/1_atk/1_atk_2.png'))
        self.v_box.add(play_2_img.with_space_around(bottom=10))
        
        play_3_img = arcade.gui.UITextureButton(x=0, y=0, texture=arcade.load_texture('assets/water/07_1_atk/1_atk_6.png'))
        self.v_box.add(play_3_img.with_space_around(bottom=10))
        
        play_4_img = arcade.gui.UITextureButton(x=0, y=0, texture=arcade.load_texture('assets/fire/11_death/death_3.png'))
        self.v_box.add(play_4_img.with_space_around(bottom=10))
        
        @start_button.event('on_click')
        def on_click_start(event):
            from main import Game
            self.manager.disable()
            game_view = Game()
            self.window.show_view(game_view)
            game_view.setup()
            
        self.manager.add(
            arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", align_y = 100, child=self.v_box))
        self.manager.add(
            arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=self.v_box2))
    
    def setup(self):
        self.background = arcade.load_texture("assets/background/background-img.jpg")
        
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)
        arcade.set_viewport(0, self.window.width, 0, self.window.height)
        

    def on_draw(self):
        self.clear()
        if not self.background:
            self.setup()
        arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        arcade.draw_text("APPLE SMASH", self.window.width/2 , 500, arcade.color.WHITE, font_size=24, anchor_x="center",)
        self.manager.draw()

    
        