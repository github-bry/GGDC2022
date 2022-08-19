import pygame
from math import sqrt
from random import randint
from random import seed


class AimJump:
    def __init__(self, screen, width, height, planet, isInner):
        seed()
        self.center_x = width / 2
        self.center_y = -800

        self.screen = screen
        self.width = width
        self.height = height

        self.shift_speed = 10
        self.current_shift = 0

        self.planets = pygame.sprite.Group()

        self.planet_name = planet
        self.planet = None

        self.landed = None

        # self.planets_list = {"Mercury": [70, 1000, 9, "Planet_Art/pMercury1.png"],
        #                      "Venus": [80, 1150, 6, "Planet_Art/pVenus.png"],
        #                      "Earth": [100, 1300, 5, "Planet_Art/pEarth.png"],
        #                      "Mars": [90, 1550, 6, "Planet_Art/pMars.png"],
        #                      "Jupiter": [100, 2000, 7, "Planet_Art/pJupiter.png"],
        #                      "Saturn": [90, 2150, 8, "Planet_Art/pSaturn2.png"],
        #                      "Uranus": [80, 2300, 5, "Planet_Art/pUranus.png"],
        #                      "Neptune": [70, 2450, 4, "Planet_Art/pNeptune.png"]}

        # width of square, radius from the center, speed

        self.planets_list = {"Mercury": [150, 1000, 9, "Planet_Art/pMercury1.png"],
                             "Venus": [200, 1500, 6, "Planet_Art/pVenus.png"],
                             "Earth": [250, 2000, 5, "Planet_Art/pEarth.png"],
                             "Mars": [200, 2500, 6, "Planet_Art/pMars.png"],
                             "Jupiter": [250, 4000, 7, "Planet_Art/pJupiter.png"],
                             "Saturn": [220, 4550, 8, "Planet_Art/pSaturn2.png"],
                             "Uranus": [180, 5100, 5, "Planet_Art/pUranus.png"],
                             "Neptune": [185, 5600, 4, "Planet_Art/pNeptune.png"]}

        inner = ["Mercury", "Venus", "Earth", "Mars"]
        outer = ["Jupiter", "Saturn", "Uranus", "Neptune"]

        # if isInner:
        #     self.add_planets(inner, planet)
        # else:
        #     self.add_planets(outer, planet)

        if not isInner:
            self.center_y -= 1000

        self.add_all_planets()

        self.player_group = pygame.sprite.Group()
        self.player = Player(30, 30, 20, self.planet)
        self.player_group.add(self.player)

        self.game_passed = False

    def add_planets(self, list, planet):
        for name in list:
            plnt = Planet(name, self.planets_list[name][0],
                          self.center_x, self.center_y,
                          self.planets_list[name][1], self.planets_list[name][2],
                          self.width, self.planets_list[name][3])
            self.planets.add(plnt)
            if name == planet:
                self.planet = plnt

    def add_all_planets(self):
        for name, specs in self.planets_list.items():
            planet = Planet(name, specs[0], self.center_x, self.center_y,
                            specs[1], specs[2], self.width, specs[3])
            self.planets.add(planet)
            if name == self.planet_name:
                self.planet = planet

    def shift(self):
        for planet in self.planets:
            self.center_y += self.current_shift
            planet.shift(self.current_shift)

    def update(self):
        """Updates the game level"""
        # updates the player - player moves
        self.player.update()
        self.planets.update()
        self.shift()

        if self.player.projected:
            if not 0 < self.player.rect.y < self.width:
                self.player.projected = False
                self.player.stop_y()
                self.player.update()
            plnts = pygame.sprite.spritecollide(self.player, self.planets, False)
            for planet in plnts:
                if planet != self.planet:
                    self.game_passed = True
                    self.landed = planet.name
                    print(self.landed)

    def key_down(self, event):
        # handles movement in four directions (using arrow keys)
        if event.key == pygame.K_UP:
            self.player.go_up()
        if event.key == pygame.K_DOWN:
            self.player.go_down()

        if event.key == pygame.K_w:
            self.current_shift = self.shift_speed
        if event.key == pygame.K_s:
            self.current_shift = -self.shift_speed

    def key_up(self, event):
        if event.key == pygame.K_w or event.key == pygame.K_s:
            self.current_shift = 0

    def display(self):
        """display everything onto the self.screen"""
        self.screen.fill((0, 0, 0))
        self.planets.draw(self.screen)
        self.player_group.draw(self.screen)

    def resized(self, event):
        # handle adjusting the size of the screen here
        # `event` will contain event.width and event.height of the new screen
        pass

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

    def passed(self):
        """return True if level is completed, False if not"""
        return self.game_passed

    def mouse_clicked(self, event):
        pass

    def mouse_released(self, event):
        pass


class Planet(pygame.sprite.Sprite):
    def __init__(self, name, size, center_x, center_y, radius, speed, screen_width, image_path="None"):
        super().__init__()
        self.name = name

        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.screen_width = screen_width
        self.change_x = speed

        if image_path == "None":
            self.image = pygame.Surface([size, size])
            self.image.fill((0, 255, 0))  # green
        else:
            self.image = self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, [size, size])

        self.rect = self.image.get_rect()
        self.rect.centerx = randint(0, screen_width)
        self.rect.centery = self.calc_y()

        self.border_constant = 20

    def calc_y(self):
        return self.center_y + sqrt(self.radius ** 2 - (self.rect.centerx - self.center_x) ** 2)

    def shift(self, change_y):
        self.center_y += change_y
        self.rect.centery = self.calc_y()

    def update(self):
        self.rect.centerx += self.change_x
        if self.rect.right > self.screen_width + self.border_constant:
            self.change_x *= -1
            self.rect.right = self.screen_width + self.border_constant
        elif self.rect.centerx < self.border_constant * -1:
            self.change_x *= -1
            self.rect.centerx = self.border_constant * -1
        self.rect.centery = self.calc_y()


class Player(pygame.sprite.Sprite):
    """ This class represents the rectangular object that the use controls. """

    def __init__(self, width, height, speed, planet_on, image_path="None"):
        super().__init__()

        if image_path == "None":
            self.image = pygame.Surface([width, height])
            self.image.fill((255, 0, 0))  # red
        else:
            self.image = self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, [width, height])

        self.planet = planet_on

        self.rect = self.image.get_rect()
        self.rect.center = planet_on.rect.center

        self.speed = speed
        self.absolute_x = None
        self.change_y = 0

        self.projected = False

    def go_up(self):
        if not self.projected:
            self.change_y = -self.speed
            self.absolute_x = self.rect.x
            self.projected = True

    def go_down(self):
        if not self.projected:
            self.change_y = self.speed
            self.absolute_x = self.rect.x
            self.projected = True

    def stop_y(self):
        self.change_y = 0

    def update(self):
        """Reserved for animations"""
        if self.projected:
            self.rect.y += self.change_y
            self.rect.x = self.absolute_x
        else:
            self.rect.center = self.planet.rect.center
