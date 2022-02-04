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
        self.v_box = arcade.gui.UIBoxLayout()
        
        
        start_button = arcade.gui.UIFlatButton(text="Start", width=150)
        self.v_box.add(start_button.with_space_around(bottom=10))
        
        @start_button.event('on_click')
        def on_click_start(event):
            from main import Game
            self.manager.disable()
            game_view = Game()
            self.window.show_view(game_view)
            game_view.setup()
            
        self.manager.add(
            arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=self.v_box))
        
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)
        arcade.set_viewport(0, self.window.width, 0, self.window.height)
        

    def on_draw(self):
        self.clear()
        arcade.draw_text("APPLE SMASH", self.window.width/2 , 380, arcade.color.WHITE, font_size=20, anchor_x="center",)
        self.manager.draw()

    
        