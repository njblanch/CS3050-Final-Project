import arcade 
import test_platformer as main
import arcade.gui
import json

SCREEN_TITLE = "Launch"

class StartButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.close_window()
        game_view = main.MyGame()
        game_view.setup()
        arcade.set_window(game_view)
        arcade.run()
        

class Title_Screen(arcade.View):
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # background
        self.background = arcade.load_texture("resources/backgrounds/supermariotitle.png")

        self.ui = arcade.gui.UIManager()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.widgets.UIBoxLayout(space_between=10)

        mario_style = {
            "font_name": "Kenney Pixel",
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": None,
        }

        one_player = StartButton(text="1 PLAYER GAME", width=200, style = mario_style)
        two_player = arcade.gui.UIFlatButton(text="2 PLAYER GAME", width=200, style=mario_style)

        self.v_box.add(one_player)
        self.v_box.add(two_player)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y", align_y= -50,
                child=self.v_box)
        )

        # Put saved stuff here
        save_name = "1"
        self.save_path = f"resources/save_data/save_{save_name}.json"
        save_file = open(self.save_path)
        save_data = json.load(save_file)
        
        self.score = save_data['score']
        self.coin_count = save_data['coin_count']
        self.lives = save_data['lives']
        self.stage = save_data['stage']
        
        save_file.close()


    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        #self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, main.SCREEN_WIDTH, main.SCREEN_HEIGHT, self.background)
        
        arcade.draw_text(self.coin_count, self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        
        draw_string = f"MARIO \t\t COINS \t\t WORLD \t\t TIME \n{self.score:06d}  \t\t {self.coin_count:02d} \t\t\t   {self.stage}"

        arcade.draw_text(draw_string,
                         main.SCREEN_WIDTH / 10,
                         main.SCREEN_HEIGHT - 2 * main.DEFAULT_FONT_SIZE,
                         arcade.color.WHITE,
                         main.DEFAULT_FONT_SIZE,
                         multiline = True,
                         width=main.SCREEN_WIDTH,
                         align="left",
                         font_name="Kenney Pixel")
        
        # manager
        self.manager.draw()


    # def on_mouse_press(self, _x, _y, _button, _modifiers):
    #     """ If the user presses the mouse button, start the game. """
    #     arcade.close_window()


        