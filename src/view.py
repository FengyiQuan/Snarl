import random
import arcade
import math
import sys

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

SCROLL_WIDTH = 512
SCROLL_HEIGHT = 384

BR_X = 64
BR_Y = 48

VIEWPORT_MARGIN = 200

MOVEMENT_SPEED = 3


class View(arcade.Window):
    def __init__(self, state):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, 'Snarl')

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.state = state

        self.player_list = None
        self.wall_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    pass

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        image_source = "images/player_1/player_stand.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """ 渲染屏幕  """

        arcade.start_render()
        # 这里是绘制屏幕的代码


def main():
    window = View(None)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
