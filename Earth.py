import pygame

from random import randint, random

class Earth():
    def __init__(self, screen, screen_h, screen_w):
        self.screen = screen
        # Height & width of visible part of minigame
        self.game_h = screen_h
        self.game_w = screen_w

        # Height & width of each lane of objects (3 total)
        self.lane_h = self.game_h // 3
        self.lane_w = self.lane_h * 150

        # Setup water
        self.water_images = []
        for i in range(16):
            self.water_images.append(pygame.image.load("Earth/water/" + str(i+1) + ".png"))
            self.water_images[i] = pygame.transform.scale(self.water_images[i], (self.game_w, self.game_h))
        
        self.water1 = Object_animated(0, 0, self.game_w, self.game_h, self.water_images, self.game_w)
        self.water2 = Object_animated(self.game_w, 0, self.game_w, self.game_h, self.water_images, self.game_w)

        # Setup players
        player_image = pygame.Surface((self.lane_h//2, self.lane_h//2))
        player_image.fill((255, 255, 255))

        self.player = Player(200, self.game_h, self.game_w, player_image, self.lane_h)

        # Sprite groups for moving objects
        self.obstacles = pygame.sprite.Group()
        self.waves = pygame.sprite.Group()
        self.all_collidable = pygame.sprite.Group()
        self.all_moving = pygame.sprite.Group(self.water1, self.water2)

        # Generate random obstacles and waves
        self.generate_map()

        # If speeding is greater than 0, the screen scrolls at a faster speed while speeding decreases
        self.speeding = 0

        self.is_passed = False

        # Record time it takes the player to complete the course
        self.start_time = pygame.time.get_ticks()
        self.total_time = 0
        self.goal_time = 40000

        # Setup text & button
        self.font = pygame.font.SysFont("Arial", self.game_h // 15)

        # Images of button
        button_still = pygame.Surface((self.game_w, self.game_h))
        button_still.fill((255, 0, 0))
        button_hover = pygame.Surface((self.game_w, self.game_h))
        button_hover.fill((255, 100, 100))

        # Properties of button
        height = self.game_h // 7
        width = height * 4
        x = self.game_w // 2
        y = self.game_h // 5 * 3

        self.button = Button(width, height, x, y, button_still, button_hover, self.font)

        self.is_paused = False


    def display(self):
        # display everything onto the self.screen

        if not self.is_paused:
            self.screen.fill((0, 0, 0))
            self.all_moving.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
        else:
            self.screen.blit(self.button.image, self.button.rect)


    def finished(self):
        # When the player reaches the finish line
        end_time = pygame.time.get_ticks()
        self.total_time = end_time - self.start_time
        if self.total_time <= self.goal_time:
            self.pause("Congradulations!", "Continue")
            self.is_passed = True
        else:
            self.pause("You were too slow!", "Start over")
            self.startover()


    def generate_map(self):
        obstacle_image = pygame.image.load("Earth/trash.png")
        obstacle_h = self.lane_h // 4 * 3 
        obstacle_w = int(obstacle_image.get_width() * (obstacle_h/obstacle_image.get_height()))
        obstacle_image = pygame.transform.scale(obstacle_image, (obstacle_w, obstacle_h))
        wave_image = pygame.image.load("Earth/wave.png")
        wave_h = self.lane_h
        wave_w = int(wave_image.get_width() * (wave_h/wave_image.get_height()))
        wave_image = pygame.transform.scale(wave_image, (wave_w, wave_h))

        # Start generating objects 4 "blocks" away from the start
        x = self.lane_h * 4
        # Generate objects at x up to x = lane_w
        while x < self.lane_w:

            # Generate up to 3 objects, 2 obstacles per column
            obs_count = 0
            for j in range(3):
                y = j * self.lane_h

                chance = random()
                # 50% chance of obstacle (up to 2), 10% chance of wave
                if obs_count < 2 and chance <= 0.5:
                    self.obstacles.add(Object(x+randint(-self.lane_h, self.lane_h), y, obstacle_w, obstacle_h, obstacle_image, self.game_w))
                    obs_count += 1
                elif chance >= 0.9:
                    self.waves.add(Object(x+randint(-self.lane_h, self.lane_h), y, wave_w, wave_h, wave_image, self.game_w))  

            # Each column is 6 "blocks" apart
            x += self.lane_h * 6
        
        # Finish line
        end_image = pygame.Surface((10, self.game_h))
        end_image.fill((0, 0, 255))

        self.end = Object(self.lane_w, 0, 10, self.game_h, end_image, self.game_w)

        self.all_collidable.add(self.waves, self.obstacles, self.end)
        self.all_moving.add(self.all_collidable)

    
    def key_down(self, event):
        # Move player according to keyboard input

        if event.key == pygame.K_UP:
            self.player.move_up()
        elif event.key == pygame.K_DOWN:
            self.player.move_down()


    def pause(self, message, button_text):
        self.is_paused = True

        # Message to display
        self.msg = self.font.render(message, True, (255, 255, 255))
        self.msg_rect = self.msg.get_rect(center = (self.game_w // 2, self.game_h // 5 * 2))

        # Text on button
        self.button.write(button_text)

        # Display
        self.screen.blit(self.msg, self.msg_rect)
        self.screen.blit(self.button.image, self.button.rect)
    

    def passed(self):
        # return True if level is completed, False if not
        return self.is_passed


    def resized(self, event):
        # handle adjusting the size of the screen here
        # `event` will contain event.width and event.height of the new screen
        pass


    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
               self.key_down(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.is_paused:
                # Check if any button was clicked
                if self.button.rect.collidepoint(event.pos):
                    self.is_paused = False


        self.update()
        self.display()

        if not self.is_paused and self.is_passed:
            return False
        else:
            return True


    def startover(self):
        # Clear everything, regenerate map, move player back to starting position

        self.player.reset()
        self.obstacles.empty()
        self.waves.empty()
        self.all_collidable.empty()
        self.all_moving.empty()

        self.all_moving.add(self.water1, self.water2)
        self.generate_map()

        self.start_time = pygame.time.get_ticks()

        self.speeding = 0


    def update(self):
        # updates the level (will be called every frame)
        # ex. Move the player, scroll the screen, generate new item

        if not self.is_paused:
            # Move the player and objects
            self.player.update()
            self.all_moving.update(self.speeding)

            # Check for collisions
            collided = pygame.sprite.spritecollideany(self.player, self.all_collidable)
            self.all_collidable.remove(collided)

            if self.obstacles.has(collided):
                # Player collided with an obstacle
                self.startover()
                self.pause("You crashed!", "Start over")
            elif self.waves.has(collided):
                # Player collided with a wave
                self.speeding += randint(100, 200)
            elif collided == self.end:
                # Player collided with the finish line
                self.finished()
            
            if self.speeding > 0:
                # Decrease speeding
                self.speeding -= 1
        else:
            self.button.update()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, game_h, game_w, image, lane_h):
        super().__init__()

        self.lane_h = lane_h
        self.game_h = game_h

        self.image = image
        # Place the player in the center of the middle lane
        self.rect = image.get_rect(midleft = (x, game_h//2))

        # Record y-coord of destination & current lane to coordinate movement between lanes
        self.move_to = self.rect.y
        self.lane = 1

        # Speed of vertical movement
        self.SPEED = game_w // 66
    

    def move_down(self):
        # Change player's destination to the lane below
        if self.lane != 2:
            self.move_to += self.lane_h
            self.lane += 1


    def move_up(self):
        # Change player's destination to the lane above
        if self.lane != 0:
            self.move_to -= self.lane_h
            self.lane -= 1


    def reset(self):
        # Move player back to the center lane
        self.rect.centery = self.game_h // 2
        self.move_to = self.rect.y
        self.lane = 1


    def update(self):
        # Move player to destinated y-coord
        distance = abs(self.move_to - self.rect.y)
        if self.move_to > self.rect.y:
            if distance > self.SPEED:
                self.rect.y += self.SPEED
            else:
                self.rect.y += distance
        elif self.move_to < self.rect.y:
            if distance > self.SPEED:
                self.rect.y -= self.SPEED
            else:
                self.rect.y -= distance


class Button(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, image_still, image_hover, font):
        """x, y are the center of the button"""

        super().__init__()

        # Setup image & rect
        self.image_still = image_still
        self.image_hover = image_hover

        self.display_still = pygame.Surface((width, height))
        self.display_hover = pygame.Surface((width, height))
        self.display_still.set_colorkey((0, 0, 0))
        self.display_hover.set_colorkey((0, 0, 0))

        self.display_still.blit(image_still, (0, 0))
        self.display_hover.blit(image_hover, (0, 0))

        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)

        # Setup text
        self.font = font
        self.text_pos = (width // 2, height // 2)

        # Display image
        self.image = self.display_still

        self.hovering = False


    def hover(self, state):
        if self.hovering != state:
            self.hovering = state
            if self.hovering:
                self.image = self.display_hover
            else:
                self.image = self.display_still
    

    def update(self):
        # Check if mouse if hovering over the button
            mouse = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse):
                self.hover(True)
            else:
                self.hover(False)

    
    def write(self, text):
        self.text = self.font.render(text, True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center = self.text_pos)

        self.display_still.blit(self.image_still, (0, 0))
        self.display_hover.blit(self.image_hover, (0, 0))

        self.display_still.blit(self.text, self.text_rect)
        self.display_hover.blit(self.text, self.text_rect)


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image, game_w):
        super().__init__()
    
        self.image = pygame.Surface((width, height))
        self.image.set_colorkey((0, 0, 0))
        self.image.blit(image, (0, 0))
        self.rect = pygame.Rect(x, y, width, height)

        # Speed of horizontal movement
        self.speed = game_w // 96
    

    def update(self, speeding):
        # Move the object left
        if speeding > 0:
            # Move 1.5x faster if in speeding mode
            self.rect.x -= int(self.speed * 1.5)
        else:
            self.rect.x -= self.speed


class Object_animated(Object):
    def __init__(self, x, y, width, height, images, game_w):
        super().__init__(x, y, width, height, images[0], game_w)

        self.game_w = game_w

        # List containing all frames of the animation
        self.images = images
        self.max_count = len(self.images) - 1

        # Set current image to the 1st
        self.image_count = 0

        # Time since the last frame was displayed
        self.time = 0

    
    def update(self, speeding):
        # Animate texture
        self.time += 1
        if self.time > 10:
            self.time = 0
            # Go to the next image in the list
            self.image_count += 1
            # Go back to the first image if all images were used
            if self.image_count > self.max_count:
                self.image_count = 0
            self.image.blit(self.images[self.image_count], (0, 0))
        
        if self.rect.right <= 0:
            self.rect.x += self.game_w * 2
        
        super().update(speeding)