import pygame
from Mars import Mars
from AimJump import AimJump

# this is a new change - Cindy
# another change - Cindy

# screen constants
screen_width = 1280
screen_height = 720


def main():
    """ Main program. """
    pygame.init()

    # Screen setup
    size = [screen_width, screen_height]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Game')

    level = Mars(screen, screen_width, screen_height, False)
    # level = AimJump(screen, screen_width, screen_height, "Earth", True)
    # levels = {"Earth": Earth(screen,)}

    # loop until the user clicks the close button
    game_over = False

    # Clock object used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # --- Main Program Loop --- #
    while not game_over:
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         game_over = True
        #
        #     if event.type == pygame.KEYDOWN:
        #         level.key_down(event)
        #
        #     if event.type == pygame.KEYUP:
        #         level.key_up(event)
        #
        #     if event.type == pygame.MOUSEBUTTONDOWN:
        #         level.mouse_clicked(event)
        #
        #     if event.type == pygame.MOUSEBUTTONUP:
        #         level.mouse_released(event)
        #
        # level.update()
        #
        # level.display()

        game_over = level.run()

        if level.game_passed:
            # move onto the next scene (dialogue or another minigame)
            pass

        # limit to 60 fps
        clock.tick(60)

        # updates the display
        pygame.display.flip()

    # Ensures the IDE quits the program once pygame is done
    pygame.quit()


if __name__ == '__main__':
    main()
