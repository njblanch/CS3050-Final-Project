import arcade
from load_textures import load_texture_pair

# Constant used for the pixel height of a tile
TILE_HEIGHT = 16

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to track if the player is sprinting
WALKING = 0
SPRINTING = 1

# Constants to check if the player is sliding
NOT_SLIDING = 0
SLIDING = 1

# Constants to track if the player is small, large, or has fire powerup
SMALL = 0
LARGE = 1
FIRE_POWERUP = 2

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 4
PLAYER_SPRINT_SPEED = 8
PLAYER_ACCELERATION = 0.2
PLAYER_FRICTION = 0.35
PLAYER_JUMP_SPEED = 18

class Mario(arcade.Sprite):
    """Player Sprite"""

    def __init__(self, scale):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.cur_grow_texture = 0
        self.scale = scale

        # Track our state
        self.sprinting = WALKING
        self.sliding = NOT_SLIDING
        self.power = SMALL
        self.is_growing = False

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = "resources/sprites/"

        # Load textures for idle standing
        self.small_idle_texture_pair = load_texture_pair(f"{main_path}mario_small_idle.png")
        self.big_idle_texture_pair = load_texture_pair(f"{main_path}mario_big_idle.png")

        # Load textures for jumping
        self.small_jump_texture_pair = load_texture_pair(f"{main_path}mario_small_jump.png")
        self.big_jump_texture_pair = load_texture_pair(f"{main_path}mario_big_jump.png")

        # Load textures for sliding
        self.small_slide_texture_pair = load_texture_pair(f"{main_path}mario_small_slide.png")
        self.big_slide_texture_pair = load_texture_pair(f"{main_path}mario_big_slide.png")

        # Load textures for walking
        self.small_walk_textures = []
        for i in range(1, 4):
            texture = load_texture_pair(f"{main_path}mario_small_walk_{i}.png")
            self.small_walk_textures.append(texture)
        self.big_walk_textures = []
        for i in range(1, 4):
            texture = load_texture_pair(f"{main_path}mario_big_walk_{i}.png")
            self.big_walk_textures.append(texture)

        # Load textures for growing
        self.grow_textures = []
        self.grow_textures.append(self.small_idle_texture_pair[0])
        self.grow_textures.append(arcade.load_texture(f"{main_path}mario_grow.png"))
        self.grow_textures.append(self.small_idle_texture_pair[0])
        self.grow_textures.append(arcade.load_texture(f"{main_path}mario_grow.png"))
        self.grow_textures.append(self.small_idle_texture_pair[0])
        self.grow_textures.append(arcade.load_texture(f"{main_path}mario_grow.png"))
        self.grow_textures.append(self.big_idle_texture_pair[0])
        # Load textures from shrinking
        self.shrink_textures = []
        self.shrink_textures.append(self.big_idle_texture_pair[0])
        self.shrink_textures.append(arcade.load_texture(f"{main_path}mario_shrink_1.png"))
        self.shrink_textures.append(self.big_idle_texture_pair[0])
        self.shrink_textures.append(arcade.load_texture(f"{main_path}mario_shrink_1.png"))
        self.shrink_textures.append(self.small_idle_texture_pair[0])
        self.shrink_textures.append(arcade.load_texture(f"{main_path}mario_shrink_2.png"))
        self.shrink_textures.append(self.small_idle_texture_pair[0])


        # Set the initial textures
        self.texture = self.small_idle_texture_pair[0]
        self.idle_textures = self.small_idle_texture_pair
        self.walk_textures = self.small_walk_textures
        self.jump_textures = self.small_jump_texture_pair
        self.slide_textures = self.small_slide_texture_pair

        # Set the height that will be used for growing
        self.grow_height = self.height * 3/2

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

        # Counter so that we can keep track of how many calls we have had to update
        self.update_counter = 0
    
    def next_power(self):
        # Mario needs to grow in size
        if self.power == SMALL:
            # Increase power
            self.power += 1
            # Change the textures we are using
            self.idle_textures = self.big_idle_texture_pair
            self.walk_textures = self.big_walk_textures
            self.jump_textures = self.big_jump_texture_pair
            self.slide_textures = self.big_slide_texture_pair
            # Change height and y val
            self.height = self.grow_height
            self.center_y += TILE_HEIGHT * self.scale * 2/3
            # Set growing var to true
            self.is_growing = True


    def prev_power(self):
        # Mario needs to shrink in size
        if self.power == LARGE:
            # Decrease power
            self.power -= 1
            # Change the textures we are using
            self.idle_textures = self.small_idle_texture_pair
            self.walk_textures = self.small_walk_textures
            self.jump_textures = self.small_jump_texture_pair
            self.slide_textures = self.small_slide_texture_pair
            # Change the height
            self.height = self.grow_height
            # Set growing var to true
            self.is_growing = True

    def powerup_animation(self):
        if self.power == LARGE:
                # Mario in growing in size
                if self.cur_grow_texture < len(self.grow_textures):
                    # Update texture every 4 updates
                    if self.update_counter % 4 == 0:
                        self.texture = self.grow_textures[self.cur_grow_texture]
                        self.cur_grow_texture += 1
                else:
                    # Mario is done growing
                    # Update Mario's height and other growing variables
                    self.cur_grow_texture = 0
                    self.height *= 4/3
                    self.is_growing = False
                return
        elif self.power == SMALL:
            # Mario is shrinking in size
            if self.cur_grow_texture < len(self.shrink_textures):
                # Update texture every 4 updates
                if self.update_counter % 4 == 0:
                    self.texture = self.shrink_textures[self.cur_grow_texture]
                    self.cur_grow_texture += 1
            else:
                # Mario is done growing
                # Update Mario's height and other growing variables
                self.cur_grow_texture = 0
                self.height *= 2/3
                self.is_growing = False
            return
        else:
            # Mario collected a fire powerup
            self.is_growing = False


    def update_movement(self, left_key_down, right_key_down, jump_key_down, sprint_key_down, physics_engine):
        # Jump if the up key is pressed
        if jump_key_down:
            if physics_engine.can_jump():
                self.change_y = PLAYER_JUMP_SPEED

        # Calculate speed based on the keys pressed
        if left_key_down and not right_key_down:
            if self.change_x > 0:
                self.sliding = SLIDING
            else:
                self.sliding = NOT_SLIDING
            if sprint_key_down:
                self.sprinting = SPRINTING
                if self.change_x > -PLAYER_SPRINT_SPEED:
                    if self.sliding:
                        self.change_x -= PLAYER_FRICTION
                    else:
                        self.change_x -= PLAYER_ACCELERATION
                elif self.change_x < PLAYER_SPRINT_SPEED:
                    self.change_x = -PLAYER_SPRINT_SPEED
            else:
                self.sprinting = WALKING
                if self.change_x > -PLAYER_MOVEMENT_SPEED:
                    if self.sliding:
                        self.change_x -= PLAYER_FRICTION
                    else:
                        self.change_x -= PLAYER_ACCELERATION
                elif self.change_x < -PLAYER_MOVEMENT_SPEED:
                    if self.change_x < -PLAYER_SPRINT_SPEED:
                        self.change_x = -PLAYER_SPRINT_SPEED
                    self.change_x += PLAYER_FRICTION
        elif right_key_down and not left_key_down:
            if self.change_x < 0:
                self.sliding = SLIDING
            else:
                self.sliding = NOT_SLIDING
            if sprint_key_down:
                self.sprinting = SPRINTING
                if self.change_x < PLAYER_SPRINT_SPEED:
                    if self.sliding:
                        self.change_x += PLAYER_FRICTION
                    else:
                        self.change_x += PLAYER_ACCELERATION
                elif self.change_x > PLAYER_SPRINT_SPEED:
                    self.change_x = PLAYER_SPRINT_SPEED
            else:
                self.sprinting = WALKING
                if self.change_x < PLAYER_MOVEMENT_SPEED:
                    if self.sliding:
                        self.change_x += PLAYER_FRICTION
                    else:
                        self.change_x += PLAYER_ACCELERATION
                elif self.change_x > PLAYER_MOVEMENT_SPEED:
                    if self.change_x > PLAYER_SPRINT_SPEED:
                        self.change_x = PLAYER_SPRINT_SPEED
                    self.change_x -= PLAYER_FRICTION
        elif self.change_x != 0:
            self.sprinting = WALKING
            self.sliding = NOT_SLIDING
            if self.change_x > 0:
                if self.change_x > PLAYER_FRICTION:
                    self.change_x -= PLAYER_FRICTION
                else:
                    self.change_x = 0
            elif self.change_x < 0:
                if self.change_x < -PLAYER_FRICTION:
                    self.change_x += PLAYER_FRICTION
                else:
                    self.change_x = 0

    def slidedown_flag(self):
        pass

    def update_animation(self, delta_time: float = 1 / 60):
        
        # Update our counter
        self.update_counter += 1

        # Check if the player is growing
        if self.is_growing:
            self.powerup_animation()
            return

        # Figure out if we need to flip face left or right
        # Only change if the player is touching the ground
        if self.change_y == 0:
            if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
                self.character_face_direction = LEFT_FACING
            elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
                self.character_face_direction = RIGHT_FACING

        # Jumping animation
        if self.change_y != 0:
            self.texture = self.jump_textures[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_textures[self.character_face_direction]
            return

        if self.sliding == SLIDING:
            self.texture = self.slide_textures[self.character_face_direction]
            return

        # Walking and sprinting animation
        if self.sprinting:
            if self.update_counter % 3 == 0:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
        else:
            if self.update_counter % 5 == 0:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
        