import pygame
from random import randint
from random import SystemRandom
from random import seed
from math import sqrt

bg_path = "Planet_Art/MarsSurface2.png"


def calc_distance(sprite1, sprite2):
    """Calculates the straight-line distance between the center of two sprites"""
    return sqrt(((sprite1.rect.centerx - sprite2.rect.centerx) ** 2) +
                ((sprite1.rect.centery - sprite2.rect.centery) ** 2))


class Mars:
    def __init__(self, screen, width, height, visible = False):
        # screen and associated dimensions
        self.screen = screen
        self.screen_width, self.screen_height = width, height

        # side length of the square in which the player can move in without scrolling the screen
        self.still_center = 300

        # radius of visible metals
        self.radius_visible = 2000
        self.radius_display = self.screen_height // 2 - 100

        # for debugging purposes
        self.visible = visible

        # bounds of the map
        self.map_width, self.map_height = 5000, 5000

        # create background
        self.bg = pygame.image.load(bg_path)
        self.bg = pygame.transform.scale(self.bg, [self.map_width, self.map_height])
        self.bg_rect = self.bg.get_rect()
        self.bg_rect.topleft = [0, 0]

        # declaration of sprite groups and other containers
        self.arrows = pygame.sprite.Group() # square hints in a circle around the player hinting at metal locations
        self.arrows_show = pygame.sprite.Group()
        self.metals = pygame.sprite.Group()
        self.spirit = None
        self.player_group = pygame.sprite.Group()

        # indicator of whether spirit has been found
        self.game_passed = False

        # declaration of player
        self.player = Player(50, 50, self.map_width // 2, self.map_height // 2, 10)
        self.player_group.add(self.player)

        # screen scrolling factors (marks where the topleft corner of the screen is)
        self.scroll_x, self.scroll_y = 0, 0

        # generates map
        self.generate_map(self.map_width, self.map_height)

        self.scrap_metal = ["Scrap Metal/Copy of can.png", "Scrap Metal/Copy of car.png",
                            "Scrap Metal/Copy of lock.png", "Scrap Metal/Copy of fuelcan.png",
                            "Scrap Metal/Copy of gears.png"]

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            if event.type == pygame.KEYDOWN:
                self.key_down(event)

            if event.type == pygame.KEYUP:
                self.key_up(event)

        self.update()

        self.display()

        return False

    def update(self):
        """Updates the game level"""
        # updates the player - player moves
        self.player.update()
        # scrolls the screen in case the player moves out of bounds
        self.scroll_screen()
        # generates the according arrows
        self.generate_arrows()

        self.arrows_show.update()

    def key_down(self, event):
        # handles movement in four directions (using arrow keys)
        if event.key == pygame.K_RIGHT:
            self.player.go_right()
        if event.key == pygame.K_LEFT:
            self.player.go_left()
        if event.key == pygame.K_UP:
            self.player.go_up()
        if event.key == pygame.K_DOWN:
            self.player.go_down()

        # w for inspecting
        if event.key == pygame.K_w:
            self.check_metal()

    def key_up(self, event):
        # if the left or right arrow has been released, then movement in the x direction should be stopped
        if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
            self.player.stop_x()
        # if the up or down arrow has been released, then movement in the y direction should be stopped
        if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
            self.player.stop_y()

    def generate_map(self, width, height, grid=700):
        seed()  # seeds random
        larger_grid = int(grid)  # set to a multiple of grid to make for potential overlap of metals
        # goes through each grid and generates a metal for each gridded section
        for i in range(0, height-larger_grid, grid):
            for j in range(0, width-larger_grid, grid):
                metal = Metal(randint(j, j+larger_grid), randint(i, i+larger_grid), 30, 30)
                self.metals.add(metal)
        # generates a spirit
        self.spirit = Metal(randint(0, width), randint(0, height), 30, 30, color=(0, 0, 255))
        self.metals.add(self.spirit)

    def generate_arrows(self):
        """Generates arrows for all metals within self.radius of the player"""
        self.arrows.empty()
        # left_border = self.player.rect.x - self.radius_display
        # right_border = self.player.rect.x + self.radius_display
        # top_border = self.player.rect.y - self.radius_display
        # bottom_border = self.player.rect.y + self.radius_display
        for metal in self.metals:
            if self.radius_display < calc_distance(metal, self.player) < self.radius_display + 10:
                print("added")
                arrow = ArrowShow(metal)
                self.arrows_show.add(arrow)
            elif self.radius_display + 10 < calc_distance(metal, self.player) <= self.radius_visible:
                # arrow = Arrow(self.screen_width, self.screen_height, self.player.rect.centerx, self.player.rect.centery,
                #               metal.rect.centerx, metal.rect.centery)
                # if not self.invisible or not (0 < metal.rect.centerx < self.screen_width and 0 < metal.rect.centery < self.screen_height):
                #     self.arrows.add(arrow)

                arrow = ArrowCircular(self.player, metal, self.radius_display)
                self.arrows.add(arrow)

    def check_metal(self):
        """Checks if the player is standing on a metal, if so, remove it"""
        metals_touched = pygame.sprite.spritecollide(self.player, self.metals, True)
        for metal in metals_touched:
            if metal == self.spirit:
                print("Spirit found")
                self.game_passed = True
            else:
                self.show_metal("Found scrap metal", self.scrap_metal)
                # show metal on screen

    def show_metal(self, message, image_paths : list):
        image_path = SystemRandom().choice(image_paths)

        display = MessageDisplay(image_path, message, self.screen_width - 300, self.screen_height - 200, 60)

        self.screen.blit(display.image, [150, 100])
        pygame.display.flip()

        pygame.time.wait(2000)


    def scroll_screen(self):
        # calculates the margins on each side
        x_margin = (self.screen_width - self.still_center) // 2
        y_margin = (self.screen_height - self.still_center) // 2

        # if the player is moving too far to the left
        if self.player.rect.x < x_margin:
            # if there is still space (the left most corner of the screen is not out of bounds)
            if not (self.scroll_x < 5):
                # move all the objects
                self.move_all(dis_x=x_margin - self.player.rect.x)
                # append the scrolling factor
                self.scroll_x -= x_margin - self.player.rect.x
                # move the player back within bounds
                self.player.rect.x = x_margin
            # if the screen cannot move and the player is approaching the border, stop it
            elif self.player.rect.x < 10:
                self.player.rect.x = 10

        # if the player is moving too far to the right
        if self.player.rect.right > self.screen_width - x_margin:
            # if there is still space
            # (the left most corner of the screen is within the width of the map - width of screen)
            if not (self.scroll_x > self.map_width - self.screen_width - 10):
                # move all objects
                self.move_all(dis_x=self.screen_width - x_margin - self.player.rect.right)
                # append the scrolling factor
                self.scroll_x -= self.screen_width - x_margin - self.player.rect.right
                # move the player back within bounds
                self.player.rect.right = self.screen_width - x_margin
            # if the screen cannot move and the player is approaching the border, stop it
            elif self.player.rect.right > self.screen_width - 10:
                self.player.rect.right = self.screen_width - 10

        # see above
        if self.player.rect.y < y_margin:
            if not (self.scroll_y < 10):
                self.move_all(dis_y=y_margin - self.player.rect.y)
                self.scroll_y -= y_margin - self.player.rect.y
                self.player.rect.y = y_margin
            elif self.player.rect.y < 10:
                self.player.rect.y = 10

        if self.player.rect.bottom > self.screen_height - y_margin:
            if not (self.scroll_y > self.map_height - self.screen_height - 10):
                self.move_all(dis_y=self.screen_height - y_margin - self.player.rect.bottom)
                self.scroll_y -= self.screen_height - y_margin - self.player.rect.bottom
                self.player.rect.bottom = self.screen_height - y_margin
            elif self.player.rect.bottom > self.screen_height - 10:
                self.player.rect.bottom = self.screen_height - 10

        # if self.player.rect.y < y_margin:
        #     self.move_all(dis_y=y_margin - self.player.rect.y)
        #     self.player.rect.y = y_margin
        # if self.player.rect.bottom > self.height - y_margin:
        #     self.move_all(dis_y=self.height - y_margin - self.player.rect.bottom)
        #     self.player.rect.bottom = self.height - y_margin

    def move_all(self, dis_x=0, dis_y=0):
        """Moves all the objects on screen"""
        for metal in self.metals:
            metal.rect.x += dis_x
            metal.rect.y += dis_y

        for arrow in self.arrows_show:
            arrow.rect.x += dis_x
            arrow.rect.y += dis_y

        self.bg_rect.x += dis_x
        self.bg_rect.y += dis_y

    def display(self):
        """display everything onto the self.screen"""
        # self.screen.fill((0, 0, 0))

        self.screen.blit(self.bg, self.bg_rect)
        if self.visible:
            self.metals.draw(self.screen)
        self.arrows.draw(self.screen)
        self.arrows_show.draw(self.screen)
        self.player_group.draw(self.screen)

    def resized(self, event):
        # handle adjusting the size of the screen here
        # `event` will contain event.width and event.height of the new screen
        pass

    def passed(self):
        """return True if level is completed, False if not"""
        return self.game_passed


class ArrowShow(pygame.sprite.Sprite):
    def __init__(self, start_sprite):
        super().__init__()

        # sets image and rect
        self.image = pygame.Surface([15, 15], pygame.SRCALPHA)

        self.colors = [(255, 255, 255, 255), (255, 255, 255, 0)]
        self.color_id = 0

        self.image.fill(self.colors[self.color_id])
        self.rect = self.image.get_rect()

        self.rect.center = start_sprite.rect.center

        self.counter = 0

        self.stop_time = 30

    def update(self):
        self.counter += 1

        if self.counter > self.stop_time:
            self.kill()

        if self.counter % 5 == 0:
            self.color_id = abs(self.color_id - 1)
            self.image.fill(self.colors[self.color_id])


class ArrowCircular(pygame.sprite.Sprite):
    def __init__(self, start_sprite, end_sprite,  radius):
        super().__init__()

        # sets image and rect
        self.image = pygame.Surface([15, 15])

        dis = calc_distance(start_sprite, end_sprite)

        self.image.fill(self.get_gradient_color(dis, radius))
        self.rect = self.image.get_rect()

        x1, y1 = start_sprite.rect.center
        x2, y2 = end_sprite.rect.center

        # set x and y as the center of the arrow
        # (x-x1)^2 + (y-y1)^2 = radius ^2 as per pythagorean theorem
        # (x2-x1)/(y2-y1) = (x-x1)/(y-y1) as per similar triangles
        # rearrange second equation to get (x-x1) = (y-y1) * (x2-x1)/(y2-y1)
        # substitute into first equation and then rearrange to get
        # (y-y1)^2 = radius^2 / (1 + [(x2-x1)/(y2-y1)]^2)
        # therefore:
        # y = y1 +- radius/(sqrt(1 + [(x2-x1)/(y2-y1)]^2))
        # x = x1 + (y-y1) * (x2-x1)/(y2-y1)

        if (y2 == y1):
            # metal and player are on the same horizontal plane
            y = y1
            if (x2 > x1):
                x = x1 + radius
            else:
                x = x1 - radius
        elif (x2 == x1):
            # metal and player are on the same vertical plane
            x = x1
            if (y2 > y1):
                y = y1 + radius
            else:
                y = y1 - radius
        else:
            A = (x2-x1) / (y2-y1)
            if (y2 > y1):
                y = y1 + radius / sqrt(1 + A ** 2)
            else:
                y = y1 - radius / sqrt(1 + A ** 2)
            x = x1 + (y-y1) * A

        self.rect.center = x, y

    def get_gradient_color(self, dis, radius):
        scale = 2000 - radius

        proximity = (dis-radius) / scale

        red = int(255 * proximity)
        green = int(255 * (1 - proximity))

        return red, green, 0


class Metal(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path="None", color=(192, 192, 192)):
        super().__init__()

        if image_path == "None":
            self.image = pygame.Surface([width, height])
            self.image.fill(color)
        else:
            self.image = self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, [width, height])

        self.rect = self.image.get_rect()

        self.rect.center = [x, y]


class MessageDisplay(pygame.sprite.Sprite):
    """
    For displaying the found metal in a picture + message format
    """
    def __init__(self, image_path, message, width, height, border, fg=(255, 255, 255), bg=(0, 0, 0)):
        """
        :param image_path: file path from directory of image
        :param message: string message to be displayed at the bottom
        :param width: width of frame
        :param height: height of frame
        :param border: border at the bottom to display image in
        """
        super().__init__()

        # larger surface for placing images on
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        # set to transparent
        self.image.fill((255, 255, 255, 0))

        # image to be loaded in from image_path
        self.image_load = pygame.image.load(image_path)
        # calculate width so that image maintains its proper scale
        # width_final = height_final * (width_original / height_original)
        img_width = (height - border) * self.image_load.get_width() / self.image_load.get_height()
        img_width = int(img_width)

        # scale the image so that the bottom strip is left out for text
        self.image_load = pygame.transform.scale(self.image_load, [img_width, height - border])

        # calculate the x margin so that the image can be blited onto the center
        x = (width - img_width) // 2

        # blit image
        self.image.blit(self.image_load, [x, 0])

        # declare font and render message
        self.font = pygame.font.SysFont("arial", 50)
        self.message = self.font.render(message, False, (255, 255, 255, 255), (0, 0, 0, 255))

        # calculate the x margin so the message can be displayed centered
        x = (width - self.message.get_width()) // 2

        # blit the message
        self.image.blit(self.message, (x, height - border))

        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    """ This class represents the rectangular object that the use controls. """

    def __init__(self, width, height, x, y, speed, image_path="None"):
        super().__init__()

        if image_path == "None":
            self.image = pygame.Surface([width, height])
            self.image.fill((0, 255, 0))  # green
        else:
            self.image = self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, [width, height])

        self.rect = self.image.get_rect()
        self.rect.center = x, y

        self.speed = speed

        self.change_x = 0
        self.change_y = 0

    def go_right(self):
        self.change_x = self.speed

    def go_left(self):
        self.change_x = -self.speed

    def go_up(self):
        self.change_y = -self.speed

    def go_down(self):
        self.change_y = self.speed

    def stop_x(self):
        self.change_x = 0

    def stop_y(self):
        self.change_y = 0

    def update(self):
        """Reserved for animations"""
        self.rect.x += self.change_x
        self.rect.y += self.change_y

# class Arrow(pygame.sprite.Sprite):
#     def __init__(self, width, height, start_x, start_y, end_x, end_y):
#         super().__init__()
#
#         # sets image and rect
#         self.image = pygame.Surface([15, 15])
#         self.image.fill((255, 0, 0))  # RED
#         self.rect = self.image.get_rect()
#
#         # set center of rect to the ending point first
#         self.rect.centerx = end_x
#         self.rect.centery = end_y
#
#         # pre-calculation for later use
#         y_diff = end_y - start_y
#         x_diff = end_x - start_x
#
#         # point is directly on top off/under the player
#         if x_diff == 0:
#             # if the point is below the player and out of bounds
#             if end_y >= height:
#                 self.rect.centerx = end_x
#                 self.rect.centery = height
#
#             if end_y <= 0:
#                 self.rect.centerx = end_x
#                 self.rect.centery = 0
#
#         # point is directly across from the player
#         elif y_diff == 0:
#             if end_x >= width:
#                 self.rect.centerx = width
#                 self.rect.centery = end_y
#
#             if end_x <= 0:
#                 self.rect.centery = end_y
#                 self.rect.centerx = 0
#
#         else:
#             # y = mx + b (m = slope, b = constant)
#             slope = y_diff / x_diff
#             constant = start_y - slope * start_x
#
#             # y = mx + b
#             if end_x >= width and 0 <= (slope * width) + constant <= height:
#                 self.rect.centerx = width
#                 self.rect.centery = slope * width + constant
#
#             if end_x <= 0 and 0 <= constant <= height:
#                 self.rect.centerx = 0
#                 self.rect.centery = constant
#
#             # x = (y - b) / m
#             if end_y >= height and 0 <= (height - constant) / slope <= width:
#                 self.rect.centerx = (height - constant) / slope
#                 self.rect.centery = height
#
#             if end_y <= 0 and 0 <= - constant / slope <= height:
#                 self.rect.centerx = - constant / slope
#                 self.rect.centery = 0
