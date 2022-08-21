import pygame
import random

ALPHA_COL = (0, 250, 0)
RED_SPOT = (250, 50, 0, 200)


class Lvl(object):
    def __init__(self, screen):
        # level stuff
        self.screen = screen
        self.running = True
        self.objects = pygame.sprite.Group()
        backgd = pygame.image.load('Images/space_backgd.png')
        self.background = pygame.transform.scale(backgd, (screen.get_width(), backgd.get_height() * (screen.get_width()/backgd.get_width())))

        # player stuff
        self.player = Player(self)
        self.player_start = [(screen.get_width() / 2) - (self.player.rect.width / 2),
                             (screen.get_height() - self.player.rect.height - int((screen.get_height() / 5)))]
        self.player_max_x = 3   # max speeds
        self.player_max_y = 9
        self.player_dist = 0   # total y dist from starting pos
        self.final_x_added = 0   # final x movement each tic

        # belt stuff
        self.num_of_belts = 30
        self.max_in_row = 6   # increase this to make it HARDER
        self.belt_x = 1920   # width and height
        self.belt_y = 200
        self.belt_min_speed = 6   # this should always be higher than player max_x
        self.belt_max_speed = 10
        self.fast_belt = self.belt_max_speed - 2   # speed that makes a belt 'fast'
        self.belts_list = []
        self.all_belts = pygame.sprite.Group()
        self.end = None   # end point (a belt)

        self.generate_map()

    def run(self):
        if self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.QUIT:
                        pygame.quit()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    else:
                        self.key_down(event)

                if event.type == pygame.KEYUP:
                    self.key_up(event)

            self.update()
            self.screen.blit(self.background, (0, 0))
            self.display()

            if self.passed():
                # move onto the next scene (dialogue or another minigame)
                self.running = False
                return False
            elif self.player.out:
                self.start_over()
                self.player.out = False
            return True

    def generate_map(self):
        """Generates all the belts, with a temp, speed, and direction."""

        # BELTS ARE GOING ACROSS THE SCREEN FROM LEFT TO RIGHT, PLAYER MOVES UP #
        for i in range(1, self.num_of_belts + 1):
            dir_lr = random.choice(["L", "R"])
            speed = random.randint(self.belt_min_speed, self.belt_max_speed)

            if i > self.max_in_row:  # after 3rd belt
                # checks if the last 3 belts were fast/slow, makes the 4th different
                num_fast = 0
                num_left = 0
                for j in range(self.max_in_row):
                    if self.belts_list[i - (j+2)][0] > self.fast_belt:
                        num_fast += 1
                    if self.belts_list[i - (j+2)][1] == "L":
                        num_left += 1
                if num_fast == self.max_in_row and speed > self.fast_belt:
                    speed = random.randint(self.belt_min_speed, self.fast_belt + 1)
                elif num_fast == 0 and speed < self.fast_belt:
                    speed = random.randint(self.fast_belt + 1, self.belt_max_speed + 1)

                if num_left == self.max_in_row and dir_lr == "L":
                    dir_lr = "R"
                if num_left == 0 and dir_lr == "R":
                    dir_lr = "L"

            self.belts_list.append([speed, dir_lr])  # temp removed

        # make all the belts
        for i in range(0, self.num_of_belts):
            belt_sprite = Belt(self.screen, self.belt_y, i, self.belts_list[i])
            self.all_belts.add(belt_sprite)

        # make red spot
        self.end = Belt(self.screen, self.belt_y, len(self.all_belts))
        self.objects.add(self.all_belts)
        self.objects.add(self.end)

    def key_down(self, event):
        """Make the player go faster, then reach max speed."""
        # goes to if statements in the player class (while faster is true,
        # increase speed every iteration)
        if event.key == pygame.K_LEFT:
            if not self.player.speed_x < -self.player_max_x:
                self.player.faster_l = True
        if event.key == pygame.K_RIGHT:
            if not self.player.speed_x > self.player_max_x:
                self.player.faster_r = True
        if event.key == pygame.K_UP:
            if not self.player.speed_y <= -1*self.player_max_y:
                self.player.faster_y = True

    def key_up(self, event):
        """Make player stop moving faster and slow down."""
        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            self.player.speed_x = 0
            self.player.faster_l = False
            self.player.faster_r = False
        if event.key == pygame.K_UP:
            self.player.speed_y = 0
            self.player.faster_y = False

    def start_over(self):
        """Reset the game if the player loses."""
        # add transition later
        self.scroll_screen(0, self.player_dist)
        self.player_dist = 0
        self.player.rect.x = self.player_start[0]
        self.player.rect.y = self.player_start[1]
        self.player.speed_x = 0
        self.player.speed_y = 0
        self.player.added_speed = 0

    def scroll_screen(self, difference, move_back=0):
        """Moves all objects if player presses up key or if start_over
        is called."""
        if move_back == 0:   # if start_over is not called
            for belt in self.objects:
                belt.rect.y += difference
        else:
            for belt in self.objects:
                belt.rect.y += move_back

    def update(self):
        """Updates the player and belts."""
        self.player.update()
        # self.check_temp()

        # keep player at start y, scroll screen
        if self.player.rect.y < self.player_start[1]:
            difference = self.player_start[1] - self.player.rect.y
            self.scroll_screen(difference)
            self.player.rect.y = self.player_start[1]
            pass

        # change player x pos, reset variable
        self.player.rect.x += self.final_x_added
        self.final_x_added = 0

        for belt in self.all_belts:
            belt.update(belt)

    def display(self):
        # only blit the belts on screen
        for belt in self.objects:
            if belt.rect.top < self.screen.get_height() and belt.rect.bottom >= 0:
                self.screen.blit(belt.image, belt.rect)
        self.screen.blit(self.player.image, self.player.rect)

    def passed(self):
        if self.player.rect.bottom < (self.end.rect.bottom - 300):
            # replace with what happens next
            return True
        else:
            return False


class Belt(pygame.sprite.Sprite):
    def __init__(self, screen, belt_y, belt_num, belt=None):
        super().__init__()
        self.screen = screen
        self.speed = None
        self.dir_lr = None
        self.arrow_anim = 0

        if belt is not None:   # for all moving belts
            # self.temp = belt[0]
            self.speed = belt[0]
            self.dir_lr = belt[1]

            # make the belt image
            self.image = pygame.Surface([self.screen.get_width(), belt_y])
            self.arrow_l = pygame.transform.scale(pygame.image.load('Images/arrow_blue.png'), (self.image.get_width() // 24,
                                                                                               self.image.get_height() // 2))
            self.arrow_r = pygame.transform.scale(pygame.image.load('Images/arrow_red.png'), (self.image.get_width() // 24,
                                                                                          self.image.get_height() // 2))

            # colours indicate direction
            if belt[1] == "L":
                self.image.blit(pygame.transform.scale(pygame.image.load('Images/blue_belt.png'), (self.image.get_width(),
                                self.image.get_height())), (0, 0))
                self.image.blit(self.arrow_l, (50, self.image.get_rect().centery - (self.arrow_l.get_height() / 2)))
            else:
                self.image.blit(pygame.transform.scale(pygame.image.load('Images/red_belt.png'), (self.image.get_width(),
                                self.image.get_height())), (0, 0))
                self.image.blit(self.arrow_r, (self.screen.get_width() - (self.arrow_r.get_width() + 50),
                                               self.image.get_rect().centery - int(self.arrow_r.get_height() / 2)))

        if belt is None:   # red spot
            self.image = pygame.Surface([self.screen.get_width(), belt_y * 5])
            spot = pygame.transform.scale(pygame.image.load('Images/red_spot.png'), [self.screen.get_width(), belt_y * 5])
            self.image.blit(spot, (0, 0))

        # create a Rect object for position
        self.rect = self.image.get_rect()
        self.rect.x = 0

        # leave a 5 px space btwn belts
        self.rect.bottom = (self.screen.get_height() - (belt_y * (belt_num-1)) - 600 - (belt_num-1)*5)

    def update(self, belt):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, level):
        """ Constructor function. """

        # call parent class constructor
        super().__init__()

        # player constants
        self.player_h = 120
        self.player_w = 80
        self.out = False  # out of bounds

        # create image of player and fill it with colour
        # could also be an image loaded from file using pygame.image.load(path)
        self.ship_img = pygame.transform.scale(pygame.image.load('Images/spaceship.png'), [self.player_w, self.player_h])
        self.fire_img = pygame.transform.scale(pygame.image.load('Images/spaceship-fire.png'), [self.player_w, self.player_h
                                                                                                // 4])
        self.image = pygame.surface.Surface([self.player_w, int(self.player_h * 1.25)])
        self.image.blit(self.ship_img, [0, 0])
        self.image.blit(self.fire_img, [0, self.player_h])

        # create a Rect object for position
        self.rect = self.ship_img.get_rect()
        self.rect.x, self.rect.y = [(level.screen.get_width() / 2) - (self.rect.width / 2),
                                    (level.screen.get_height() - self.rect.height - int(
                                        (level.screen.get_height() / 5)))]

        # set speed vector for player
        self.speed_x = 0
        self.speed_y = 0
        self.speed_increment = 0.5
        self.faster_l = False
        self.faster_r = False
        self.faster_y = False
        self.slow_y = False
        self.added_speed = 0

        # connect player to level
        self.level = level

    def update(self):
        """Overwriting the update() function of parent class. Changes player speed."""

        # speed up or slow down player by square (nice movement feel)
        if self.faster_r and self.speed_x <= self.level.player_max_x:
            self.speed_x += self.speed_increment ** 2
        elif self.faster_l and self.speed_x >= -self.level.player_max_x:
            self.speed_x -= self.speed_increment ** 2
        elif self.faster_y and self.speed_y >= -self.level.player_max_y:
            self.speed_y -= self.speed_increment ** 2
        elif self.slow_y:
            self.speed_y += self.speed_increment ** 2

        # stop speeding up when at max speed
        if self.speed_x >= self.level.player_max_x:
            self.faster_l = False
            self.faster_r = False
            self.speed_x = self.level.player_max_x
        elif self.speed_x <= -self.level.player_max_x:
            self.faster_l = False
            self.faster_r = False
            self.speed_x = -self.level.player_max_x
        elif self.speed_y <= -1*self.level.player_max_y:
            self.faster_y = False
            self.speed_y = -self.level.player_max_y

        # add arrow key speed to final speed
        self.level.final_x_added += self.speed_x

        # get belt modifications
        belt_hit_list = pygame.sprite.spritecollide(self, self.level.all_belts, False)
        if len(belt_hit_list) == 2:
            for belt in belt_hit_list:
                # get the speed of the top belt
                if belt.rect.bottom > self.rect.top:
                    # add belt speed to final speed
                    if hasattr(belt, 'dir_lr') and hasattr(belt, 'speed'):
                        if belt.dir_lr == "L":
                            self.added_speed = -belt.speed
                        else:
                            self.added_speed = belt.speed
        elif len(belt_hit_list) == 1:   # to catch all instances
            for belt in belt_hit_list:
                if hasattr(belt, 'dir_lr') and hasattr(belt, 'speed'):
                    if belt.dir_lr == "L":
                        self.added_speed = -belt.speed
                    else:
                        self.added_speed = belt.speed

        # when player is at the end
        if pygame.sprite.spritecollide(self, pygame.sprite.Group(self.level.end), False):
            self.added_speed = 0
        else:   # add final speed to player movement
            self.level.final_x_added += self.added_speed

        # update the position of the rect with the speed
        self.rect.y += round(self.speed_y)
        self.level.player_dist += round(self.speed_y)

        # check if player is out of bounds
        if self.rect.right < 0:
            self.out = True
        elif self.rect.left > self.level.screen.get_width():
            self.out = True

        self.fire_anim()

    def fire_anim(self):
        fire_scaled = pygame.transform.scale(self.fire_img, [self.player_w, int((self.player_h // 4) *
                                                             (abs(self.speed_y / self.level.player_max_y)) ** .20)])
        self.image.fill(ALPHA_COL)
        self.image.set_colorkey(ALPHA_COL)
        self.image.blit(self.ship_img, (0, 0))
        self.image.blit(fire_scaled, (0, self.player_h))
