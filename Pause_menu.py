import pygame

class Pause_menu():
    def __init__(self, screen, screen_w, screen_h):
        # Screen constants
        self.screen = screen

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.is_passed = False

        # Title text
        title_font = pygame.font.SysFont("Arial", int(self.screen_h // 7))
        self.title_text = title_font.render("Paused", True, (255, 255, 255))

        title_x = self.screen_w // 2
        title_y = self.screen_h // 4
        self.title_rect = self.title_text.get_rect(center = (title_x, title_y))

        # Sprite group to hold all buttons
        self.buttons = pygame.sprite.Group()

        # --- Start button --- #
        # Size & pos
        height = self.screen_h // 7
        width = height * 4
        x = self.screen_w // 2
        y = self.screen_h // 5 * 3

        # Images
        still = pygame.image.load("UI/button.png")
        still = pygame.transform.scale(still, (width, height))
        hover = pygame.image.load("UI/button_hover.png")
        hover = pygame.transform.scale(hover, (width, height))

        # Text
        font = pygame.font.SysFont("Arial", int(height * 0.6))
        text = "Continue"

        self.start_button = Button(width, height, x, y, still, hover, font, text)

        self.buttons.add(self.start_button)

        # --- Exit button --- #
        # Size & pos
        # height = self.screen_h // 7
        # width = height * 4
        x = self.screen_w // 2
        y = self.screen_h // 5 * 4

        # Images
        # still = pygame.image.load("Main_menu/button.png")
        # still = pygame.transform.scale(still, (width, height))
        # hover = pygame.image.load("Main_menu/button_hover.png")
        # hover = pygame.transform.scale(hover, (width, height))

        # Text
        font = pygame.font.SysFont("Arial", int(height * 0.6))
        text = "Exit"

        self.exit_button = Button(width, height, x, y, still, hover, font, text)

        self.buttons.add(self.exit_button)

        # --- Credits button --- #
        # Size & pos
        height = self.screen_h // 7
        width = height
        x = self.screen_w // 2 + width*3
        y = self.screen_h // 5 * 4

        # Images
        still = pygame.image.load("UI/button_circle.png")
        still = pygame.transform.scale(still, (width, height))
        hover = pygame.image.load("UI/button_circle_hover.png")
        hover = pygame.transform.scale(hover, (width, height))

        # Text
        font = pygame.font.SysFont("Arial", int(height * 0.3))
        text = "Credits"

        self.credits_button = Button(width, height, x, y, still, hover, font, text)

        self.buttons.add(self.credits_button)

        # Display title
        self.screen.blit(self.title_text, self.title_rect)


    def clicked(self, button):
        if button == self.start_button:
            # Continue game
            print("continue")
        elif button == self.exit_button:
            # Exit game
            print("exit")
            self.is_passed = True
        elif button == self.credits_button:
            # Credits
            print("credits")


    def display(self):
        # Draw buttons
        self.buttons.draw(self.screen)


    def run(self):

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any button was clicked
                click = event.pos
                for button in self.buttons:
                    if button.rect.collidepoint(click):
                        self.clicked(button)
        
        self.update()
        self.display()

        if self.is_passed:
            return False
        else:
            return True
    

    def update(self):
        # Update buttons
        self.buttons.update()


class Button(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, image_still, image_hover, font, text):
        """x, y are the center of the button"""

        super().__init__()

        # Setup image & rect
        self.image_still = pygame.Surface((width, height))
        self.image_hover = pygame.Surface((width, height))

        self.image_still.blit(image_still, (0, 0))
        self.image_hover.blit(image_hover, (0, 0))

        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)

        # Setup text
        self.text = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center = (width // 2, height // 2))

        self.image_still.blit(self.text, self.text_rect)
        self.image_hover.blit(self.text, self.text_rect)

        # Display image
        self.image = self.image_still

        self.hovering = False


    def hover(self, state):
        if self.hovering != state:
            self.hovering = state
            if self.hovering:
                self.image = self.image_hover
            else:
                self.image = self.image_still
            

    def update(self):
        # Check if mouse if hovering the button
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover(True)
        else:
            self.hover(False)

