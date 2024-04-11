"""
Platformer Template
"""
import arcade
import time
import math
import launch
import random
from mario import Mario
from enemy import Enemy
#from enemy import GoombaEnemy
import json
from mystery_box import Mystery_Box
from coin import Coin
from load_textures import load_texture_pair


# --- Constants
SCREEN_TITLE = "Platformer"

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 600
DEFAULT_FONT_SIZE = 25
INTRO_FRAME_COUNT = 150

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 2.5
TILE_SCALING = 2.5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING
NUMBER_OF_COINS = 3

# The gravity that is used by the physics engine
GRAVITY = 0.8

PLAYER_START_X = SPRITE_PIXEL_SIZE * CHARACTER_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 2

LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_PLATFORMS_BREAKABLE = "Platform_Breakable"
LAYER_NAME_PLATFORMS_COINS = "Platform_Coin"
LAYER_NAME_PLATFORMS_ITEM = "Platform_Item"
LAYER_NAME_MYSTERY_ITEM = "Mystery_Item"
LAYER_NAME_MYSTERY_COIN = "Mystery_Coin"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_FLAG = "Flag"
LAYER_NAME_ENEMIES = "enemies"
LAYER_NAME_TELEPORT_EVENT = "Teleport"
LAYER_NAME_DOOR = "Next_Level_Door"

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT,
                         SCREEN_TITLE, resizable=False)

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

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.mario = None

        self.mario_door = False

        self.mario_flag = False

        # Our physics engine
        self.physics_engine = None

        self.background_list = []

        self.player_list = []

        self.enemy_list = []

        # -- sounds --
        self.jump_sound = arcade.load_sound("resources/sounds/jump_sound.mp3")

        self.coin_sound = arcade.load_sound("resources/sounds/smw_coin.wav")

        self.timeUp = arcade.load_texture("resources/backgrounds/timeupMario.png")

        # A Camera that can be used for scrolling the screen
        self.camera = None

        self.screen_center_x = 0
        self.screen_center_y = 0

        # What key is pressed down?
        self.left_key_down = False
        self.right_key_down = False
        self.jump_key_down = False
        self.sprint_key_down = False

        # different levels
        self.stages = {1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "2-1", 6: "2-2", 7: "2-3", 8: "2-4"}
        self.stage_num = 1
        self.mario_world = 0
        self.success_map = False

        # background color
        arcade.set_background_color(arcade.color.BLACK)
        
        self.background = arcade.load_texture("resources/backgrounds/supermariostagestart.png")

        

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        
        # Store the save file, as the player has either died or gotten to
        # a new stage        
        self.save()
        
        self.stage_intro = True
        
        self.timer = 300
        self.frame_counter = 0
        
        # Reset the 'center' of the screen to 0
        self.screen_center_x = 0
        self.screen_center_y = 0
        
        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)
        
        player_centered = self.screen_center_x, self.screen_center_y

        self.camera.move_to(player_centered)
        
        
    def setup_part_2(self):
        
        self.do_update = True
        # Initialize the set for handling when blocks are nudged
        self.nudged_blocks_list_set = ([],[],[],[],[])
                
        # Reset the frame counter
        self.frame_counter = 0

        map_name = self.next_world()

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
            },
            LAYER_NAME_PLATFORMS_BREAKABLE: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
            },
            LAYER_NAME_PLATFORMS_COINS: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
            },
            LAYER_NAME_PLATFORMS_ITEM: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
            },
            LAYER_NAME_MYSTERY_ITEM: {
                "use_spatial_hash": True,
                "custom_class": Mystery_Box,
            },
            LAYER_NAME_MYSTERY_COIN: {
                "use_spatial_hash": True,
                "custom_class": Mystery_Box,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
                "custom_class": Coin,
            },
            LAYER_NAME_BACKGROUND: {
                "use_spatial_hash": True,
            },
             LAYER_NAME_ENEMIES: {
                 "use_spatial_hash": True,
                 #"custom_class": GoombaEnemy,
                 "enemies": {
                   "custom_class": Enemy
                 },
             },
            LAYER_NAME_FLAG: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DOOR: {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map        
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        #self.tile_map = arcade.load_tilemap(f'map{self.level}.tmx', layer_options= layer_options)        

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set platforms
        self.platform_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS]
        self.platform_breakable_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS_BREAKABLE]
        self.platform_coin_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS_COINS]
        self.platform_item_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS_ITEM]
        self.mystery_item_list = self.tile_map.sprite_lists[LAYER_NAME_MYSTERY_ITEM]
        self.mystery_coin_list = self.tile_map.sprite_lists[LAYER_NAME_MYSTERY_COIN]
        self.enemy_list = self.tile_map.sprite_lists[LAYER_NAME_ENEMIES]

        # Set coins
        self.coin_list = self.tile_map.sprite_lists[LAYER_NAME_COINS]

        # flag tiles
        self.flag_list = self.tile_map.sprite_lists[LAYER_NAME_FLAG]

        # Set background image
        self.background_list = self.tile_map.sprite_lists[LAYER_NAME_BACKGROUND]

        # door tile
        self.door = self.tile_map.sprite_lists[LAYER_NAME_DOOR]

        # Set the position of the background

        # Calculate the drawing position for the background sprite
        background_draw_x = self.tile_map.width*GRID_PIXEL_SIZE / 2
        background_draw_y = self.tile_map.height*GRID_PIXEL_SIZE / 2 # Align top of sprite with top of screen
        self.background_list[0].set_position(background_draw_x, background_draw_y)

        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # -- Enemies
        # for my_object in enemies_layer:
        #     cartesian = self.tile_map.get_cartesian(
        #         my_object.shape[0], my_object.shape[1]
        #     )

        #     #todo: enemy_type== "goomba" might not work!!
        #     #enemy_type = my_object.properties["type"]
        #     #if enemy_type == "goomba":
        #         #enemy = GoombaEnemy()
        #     #elif enemy_type == "zombie":
        #         #enemy = ZombieEnemy()
        #     #else:
        #         #raise Exception(f"Unknown enemy type {enemy_type}.")
            
        #     goomba = GoombaEnemy()
        #     # Set the initial position of the Goomba
        #     goomba.center_x = 55  # Set the x-coordinate according to your game's layout
        #     goomba.center_y = 48  # Set the y-coordinate according to your game's layout
        #     # Add the Goomba to the appropriate sprite list
        #     self.scene.add_sprite(LAYER_NAME_ENEMIES, goomba)

        #     '''
        #     enemy.center_x = math.floor(
        #         cartesian[0] * TILE_SCALING * self.tile_map.tile_width
        #     )
        #     enemy.center_y = math.floor(
        #         (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
        #     )
        #     '''
        #     self.scene.add_sprite(LAYER_NAME_ENEMIES, goomba)

        # Set up the player, specifically placing it at these coordinates.
        self.mario = Mario(CHARACTER_SCALING)
        self.mario.center_x = 48
        self.mario.center_y = 48
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.mario)

        # --- Other stuff
        # Create the 'physics engine'
        walls = [self.platform_list, self.platform_breakable_list, self.platform_item_list, self.mystery_item_list, self.mystery_coin_list]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.mario, gravity_constant=GRAVITY, walls=walls
        )
        self.success_map = False


    def on_draw(self):
        """Render the screen."""
        # Clear the screen to the background color
        self.clear()
        
        # Activate our Camera
        self.camera.use()
        
        if self.stage_intro:
            
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
            
            draw_string = f"WORLD  {self.stage}\n\n\t\t{self.lives}"
            
            self.draw_text()
            
            arcade.draw_text(draw_string,
                             self.screen_center_x,
                             self.screen_center_y + SCREEN_HEIGHT/2 + 3*DEFAULT_FONT_SIZE,
                             arcade.color.WHITE,
                             DEFAULT_FONT_SIZE * 1.5,
                             multiline = True,
                             width=SCREEN_WIDTH,
                             align="center",
                             font_name="Kenney Pixel")
            
            return
        
        
        # Draw our Scene
        # Draw the platforms
        self.scene.draw(pixelated=True)

        #Todo: Draw the goombas

        # Draw the player
        self.mario.draw(pixelated=True)
        
        self.draw_text()
        
    def draw_text(self):
        # Draw the text last, so it goes on top
        # Have to squeeze everything into one text draw, otherwise major lag
        draw_string = f"MARIO \t\t COINS \t\t WORLD \t\t TIME \n{self.score:06d}  \t\t {self.coin_count:02d} \t\t\t   {self.stage} \t\t {self.timer:03d}"
        
        arcade.draw_text(draw_string,
                         self.screen_center_x + SCREEN_WIDTH / 10,
                         SCREEN_HEIGHT - 2 * DEFAULT_FONT_SIZE,
                         arcade.color.WHITE,
                         DEFAULT_FONT_SIZE,
                         multiline = True,
                         width=SCREEN_WIDTH,
                         align="left",
                         font_name="Kenney Pixel")
        
        if self.timer <= 0:
            arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.timeUp)
    

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        # Make sure that we are supposed to be doing updates
        if self.stage_intro:
            return
        
        # Jump
        if key == arcade.key.UP or key == arcade.key.W:
            self.jump_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            # Prevents the user from double jumping
            self.jump_key_down = False
            arcade.play_sound(self.jump_sound)
        # Left
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
        # Right
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
        # Sprint
        elif key == arcade.key.J:
            self.sprint_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            
        # Reset
        elif key == arcade.key.ESCAPE:
            self.player_die()


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
        elif key == arcade.key.J:
            self.sprint_key_down = False

    def center_camera_to_player(self):
        if (self.mario.center_x - (self.camera.viewport_width / 3)) > self.screen_center_x:
            self.screen_center_x = self.mario.center_x - (self.camera.viewport_width / 3)

        # Don't let camera travel past 0
        if self.screen_center_x < 0:
            self.screen_center_x = 0

        player_centered = self.screen_center_x, self.screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):

        # Only display the intro during the intro
        if self.stage_intro:
            self.frame_counter += 1
            
            if self.frame_counter == INTRO_FRAME_COUNT or self.success_map:
                self.stage_intro = False
                self.setup_part_2()
                
            return # Early return
        
        # Make sure that we are supposed to be doing updates
        if self.do_update:
            """Movement and game logic"""
            if self.mario.center_x < self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2:
                self.mario.center_x = self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2
                self.mario.change_x = 0
            
            
            self.frame_counter += 1
            if self.frame_counter > 20:
                self.timer -= 1
                self.frame_counter = 0
            
            
            # Player dies if they fall below the world or run out of time
            if self.mario.center_y < -SPRITE_PIXEL_SIZE:
                self.player_die()
                
        
            # Player movement and physics engine
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            self.physics_engine.update()

            # Update Animations
            if not self.mario_flag:
                self.scene.update_animation(
                    delta_time, [LAYER_NAME_PLAYER, LAYER_NAME_MYSTERY_COIN, LAYER_NAME_MYSTERY_ITEM, LAYER_NAME_COINS, LAYER_NAME_ENEMIES]
                )
            else:
                self.scene.update_animation(
                    delta_time, [LAYER_NAME_MYSTERY_COIN, LAYER_NAME_MYSTERY_ITEM, LAYER_NAME_COINS]
                )

            # Position the camera
            self.center_camera_to_player()


            # if get to flagpole
            if arcade.check_for_collision_with_list(self.mario, self.flag_list):
                # call animation method
                self.mario_flag = True
            else:
                self.mario_flag = False

            if self.mario_flag:
                self.mario.slidedown_flag()
                self.mario_door = True

            if self.mario_door:
                self.flag_animation()

            self.door_hit = arcade.check_for_collision_with_list(self.mario, self.door)

            if self.door_hit:
                self.mario.visible = False
                

            # See if the coin is touching mario
            coin_hit_list = arcade.check_for_collision_with_list(self.mario, self.coin_list)
            
            for coin in coin_hit_list:
                #self.do_update = False
                # if self.mario.power == 0:
                #     self.mario.next_power()
                # else:
                #     self.mario.prev_power()
                self.coin_count += 1
                # Remove the coin
                coin.remove_from_sprite_lists()
                # Play a sound
                arcade.play_sound(self.coin_sound)
  
            # Proof of concept of hitting the above block:
            # Testing with breakable blocks first
            height_multiplier = int(self.mario.power > 0) + 1
            
            # Get the block list for the left side of mario's head
            block_hit_list = arcade.get_sprites_at_point((self.mario.center_x - 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.platform_breakable_list)
           
            # Add to that list the blocks on the right side of mario's head
            block_hit_list.extend(arcade.get_sprites_at_point((self.mario.center_x + 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.platform_breakable_list))
           
            # Turn that list into a set to eliminate duplicate valuesgit 
            block_hit_list = set(block_hit_list)

            # Later, add a requisite that the mario must be big
            for block in block_hit_list:
                # Perhaps change this to a call to a function that activates some block_break
                # event at the position of each broken block
                # Remove the block
                if self.mario.power > 0:
                    block.remove_from_sprite_lists()
                
                else:
                    # This means Mario is small, bump the block!
                    self.nudged_blocks_list_set[4].append(block)
                
                # Play a sound (change to breaking sound)
                # arcade.play_sound(self.coin_sound)


            # Define the range of x-coordinates
            x_range = range(int(self.mario.center_x) - 16, int(self.mario.center_x) + 17)  # Extend range by 1 to include both end points

            # Iterate over each x-coordinate in the range
            for x in x_range:
                # Call get_sprites_at_point for each x-coordinate
                enemy_hit_list = arcade.get_sprites_at_point((x, self.mario.center_y - height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 - 2), self.enemy_list)
                for enemy in enemy_hit_list:
                    #todo: at the position where the enemy was, put in the new sprite #get_sprite_at_point
                    enemy.remove_from_sprite_lists()

            #mushroom kills mario- todo: fix this so jumping on top doesn't kill mario
            mario_list = arcade.check_for_collision_with_list(self.mario, self.enemy_list) #change ot enemy_hit_list?
            #check if there is anything in the list, if not, 
            if mario_list:
                self.player_die()


    def nudge_blocks(self):
        # On every few frames, allow the nudged blocks to move
        if self.frame_counter % 3 == 0:
            temp_nudged_blocks_list_set = ([],[],[],[],[])
            for list_id, nudged_block_list in enumerate(self.nudged_blocks_list_set):
                for block in nudged_block_list:
                    # Add the index of the list the block is in, centered around
                    # the middle list (by subtracting the length less 1, over 2)
                    # This achieves the effect of going up and down in equal amounts
                    # The multiplication gives a larger magnitude to the effect
                    block.center_y += (list_id - 2) * 2
                    
                    # If the block is not in the final (lowest)
                    if list_id-1 >= 0:
                        # Put the block in a lower list
                        temp_nudged_blocks_list_set[list_id-1].append(block)
                    # Otherwise, do not put the block back in any nudging list
                    
                self.nudged_blocks_list_set = temp_nudged_blocks_list_set
    
    
    def flag_animation(self):
        if self.mario.center_y > SPRITE_PIXEL_SIZE * TILE_SCALING * 4:
            self.mario.slidedown_flag()
        else:
            if not arcade.check_for_collision_with_list(self.mario, self.door):
                self.mario.walk_to_door()
            else:
                self.mario_door = False
                self.stage_num += 1
                self.next_world()
                self.setup_part_2()


    def next_world(self):
        # Name of map file to load
        self.mario_world = self.stages[self.stage_num]
        print("stage is: ", self.mario_world)
        map_name = f"resources/backgrounds/{self.mario_world}/world_{self.mario_world}.json"
        success_map = True
        return map_name

        
    def save(self):
        save_file = open(self.save_path, "w")
        save_data = {
            'score' : self.score,
            'coin_count' : self.coin_count,
            'lives' : self.lives,
            'stage' : self.stage
        }
        json.dump(save_data, save_file)        
        save_file.close()
        
    def player_die(self):
        self.lives -= 1
        # Can likely put these at the start of setup:
            # Give a death screen
        
        # Set the timer and position to be safe, so it is not called again
        self.timer = 10
        self.mario.set_position(0, 2*SCREEN_HEIGHT)
        
        # For later, give a game over screen if lives reduced to zero (>0 can be infinite)
        # Ideally, also reset the save file to a default version (save_0.json)
        if self.lives == 0:
            pass
        
        
        # Reset the stage
        self.setup()


def main():
    """Main function"""
    # window = MyGame()
    # window.setup()
    # arcade.run()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = launch.Title_Screen()
    window.show_view(start_view)
    arcade.run()
    # arcade.close_window()


if __name__ == "__main__":
    main()