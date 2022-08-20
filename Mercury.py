import pygame

from random import randint

class Mercury():
    def __init__(self, screen, screen_h, screen_w):
        self.screen = screen
        # Height & width of visible part of minigame
        self.game_h = screen_h
        self.game_w = screen_w

        # Background image
        self.background = pygame.image.load("Mercury/mercury-pix2.png")
        self.background = pygame.transform.scale(self.background, (screen_w, screen_h))

        # Images containing the tiles to build the moving ridges and mountains
        self.ridge_images = pygame.image.load("Mercury/ridges.png")
        self.mount_images = pygame.image.load("Mercury/props.png")

        # Size & location of each tile in the above images
        self.ridge_sizes = (15, 32, 16, 16, 32, 32, 32, 15)
        self.ridge_x = [0]
        self.ridge_count = len(self.ridge_sizes)
        for i in range(self.ridge_count - 1) :
            self.ridge_x.append(self.ridge_x[i] + self.ridge_sizes[i] + 16)

        self.mount_sizes = (139, 160, 99, 173, 48, 94, 58, 117, 109, 65)
        self.mount_x = [0]
        self.mount_count = len(self.mount_sizes)
        for i in range(self.mount_count - 1) :
            self.mount_x.append(self.mount_x[i] + self.mount_sizes[i] + 16)

        # Default colors of the above images
        self.ridge_color = (15, 7, 13)
        self.mount_color = (20, 16, 18)

        # Sprite groups holding moving objects
        self.ridges = pygame.sprite.Group()
        self.mounts = pygame.sprite.Group()
        self.all_moving = pygame.sprite.Group()

        # Height & y-coord of the ground
        self.ground_h = self.game_h // 4
        self.ground_y = self.game_h - self.ground_h

        # Width of each tile
        self.tile_w = self.game_w // 10
        # Scale factor - for each 16-pixel wide ridge to be scaled up to tile_w
        self.scale_factor = self.tile_w / 16

        # Length of the course
        self.length = self.game_w * 20

        # Control speed of horizonal movement
        self.speed1 = self.game_w // 48
        # Slower speed for objects farther away
        self.speed2 = self.speed1 // 10

        self.generate_map()

        player_image = pygame.Surface((self.ground_h//2, self.ground_h//2))
        player_image.fill((255, 255, 255))

        self.player = Player(100, self.ground_y, player_image, self.game_w)

        # Setup pause screen
        # Text
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

        self.is_passed = False
        self.is_paused = False
        


    def display(self):
        # display everything onto the self.screen

        if not self.is_paused:
            self.screen.blit(self.background, (0, 0))
            self.all_moving.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
        else:
            self.screen.blit(self.button.image, self.button.rect)


    def generate_map(self):
        # Generate ridges
        x = 0
        while x < self.length:
            
            x += self.place_ridge(0, x)
            # Generate a ridge 2 - 5 tiles long
            for i in range(randint(1, 5)) :
                # Choose a random ridge image that's not the first or last image & place
                x += self.place_ridge(randint(1, len(self.ridge_sizes) - 2), x)
            x += self.place_ridge(len(self.ridge_sizes)-1, x)

            # Generate a gap 3 - 7 tiles long
            for i in range(randint(3, 7)):
                x += self.tile_w
        
        # Generate mountains
        x = 0
        while x < self.length:
            # Choose a random mountain image
            choice = randint(0, len(self.mount_sizes) - 1)
            mount_image = pygame.Surface((self.mount_sizes[choice], 143))   # Tallest mount is 143 pixels
            mount_image.set_colorkey(0)
            mount_image.blit(self.mount_images, (0, 0), (self.mount_x[choice], 0, self.mount_sizes[choice], 143))
            # Scale mount image
            mount_image = pygame.transform.scale(mount_image, (self.mount_sizes[choice] * self.scale_factor // 1.5, 143 * self.scale_factor // 1.5))
            # Place the mountain in the map
            self.mounts.add(Object(x, self.game_h - 143*self.scale_factor // 1.5, mount_image, self.speed2))

            gap = randint(2, 6)
            x += self.tile_w * gap

        # Finish line
        end_image = pygame.Surface((10, self.game_h))
        end_image.fill((0, 0, 255))

        self.end = Object(self.length, 0, end_image, self.speed1)

        self.all_moving.add(self.mounts, self.ridges, self.end)


    def key_down(self, event):
        if event.key == pygame.K_UP:
            self.player.jump()


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
        return self.is_passed


    def place_ridge(self, choice, x):
        # Return the change in x. choice: index value of chosen ridge

        ridge_size = self.ridge_sizes[choice]
        ridge_image = pygame.Surface((ridge_size, 33))    # Each ridge image is 33 pixels tall
        ridge_image.set_colorkey((0, 0, 0))
        ridge_image.blit(self.ridge_images, (0, 0), (self.ridge_x[choice], 0, ridge_size, 33))    # Area = (x, y, width, height)
        # Scale ridge image
        ridge_image = pygame.transform.scale(ridge_image, (int(ridge_size * self.scale_factor), int(33 * self.scale_factor)))
        # Put the ridge in the map
        self.ridges.add(Object(x, self.ground_y, ridge_image, self.speed1))

        return ridge_image.get_width()
    

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
        # Clear everything
        self.player.reset()
        self.ridges.empty()
        self.mounts.empty()
        self.all_moving.empty()

        # Reset speed of sprites
        for sprite in self.ridges:
            sprite.speed = self.speed1
        for sprite in self.mounts:
            sprite.speed = self.speed2
        self.end.speed = self.speed1

        # Regenerate map
        self.generate_map()
        self.end.rect.x = self.length


    def update(self):
        # updates the level (will be called every frame)
        # ex. Move the player, scroll the screen, generate new item

        if not self.is_paused:
            # Move the player in the vertical direction
            self.player.update()

            # Player collides with the ground
            if pygame.sprite.spritecollideany(self.player, self.ridges):
                self.player.hit_ground(self.ground_y)

            # Move the objects on screen in the horizontal direction
            self.all_moving.update()

            # Player collides with the side of a ridge
            if pygame.sprite.spritecollideany(self.player, self.ridges):
                self.startover()
                self.pause("You crashed!", "Startover")

            # Player collides with finish line
            if pygame.sprite.collide_rect(self.player,self.end):
                # Player collided with the finish line
                self.pause("Congratulations!", "Continue")
                self.is_passed = True
            
            # Player falls to the bottom of screen
            if self.player.rect.bottom > self.game_h:
                self.startover()
                self.pause("You fell!", "Startover")
        else:
            self.button.update()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image, game_w):
        super().__init__()

        self.image = image
        self.rect = image.get_rect(bottomleft = (x, y))
        self.y = y

        # Control player's vertical speed
        self.speed_y = 0
        self.gravity = game_w // 200
        self.jump_power = game_w // 25

        # Player can jump twice before hitting the ground again
        self.jumps = 0
    

    def update(self):
        # Move player
        self.rect.bottom -= self.speed_y
        # Accelerate player toward ground
        self.speed_y -= self.gravity
    

    def jump(self):
        if self.jumps < 2:
            self.speed_y = self.jump_power
            self.jumps += 1
    

    def hit_ground(self, y):
        # Stop the player from moving farther down
        self.speed_y = 0
        self.rect.bottom = y
        # Reset the number of jumps
        self.jumps = 0
    

    def reset(self):
        self.rect.bottom = self.y

        self.speed_y = 0
        self.jumps = 0


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
    def __init__(self, x, y, image, speed):
        super().__init__()

        self.image = image
        self.rect = image.get_rect(topleft = (x, y))
        self.speed = speed
    

    def update(self):
        # Move the object left
        self.rect.x -= self.speed

        # Kill off-screen objects
        if self.rect.right < 0:
            self.kill()
