# UtilSpriteSheetGrid.py
import pygame
# Font

    
# DisplayGrid
# This function loads a spritesheet, and displays them all in a grid. It shows the grid coordinates for each sprite.
# This is useful for figuring out the coordinates of sprites in a spritesheet.
# Offset is an (x, y) tuple that is added to the coordinates of each sprite.
def displayGrid(filename, tileSize, offset, transparentColor, window):
    pygame.font.init()

    # Load the spritesheet
    spritesheet = pygame.image.load(filename).convert()
    spritesheet.set_colorkey(transparentColor)

    # Display the spritesheet
    window.blit(spritesheet, (0, 0))

    # Display the grid
    for y in range(0, spritesheet.get_height(), tileSize[1]):
        pygame.draw.line(window, (255, 255, 255), (0 + offset[0], y + offset[1]), (spritesheet.get_width(), y + offset[1]))
    for x in range(0, spritesheet.get_width(), tileSize[0]):
        pygame.draw.line(window, (255, 255, 255), (x + offset[0], 0 + offset[1]), (x + offset[0], spritesheet.get_height()))

    # Display the grid coordinates
    font = pygame.font.SysFont("Arial", 8)
    for y in range(0, spritesheet.get_height(), tileSize[1]):
        for x in range(0, spritesheet.get_width(), tileSize[0]):
            text = font.render(str(x // tileSize[0]) + "," + str(y // tileSize[1]), True, (255, 255, 255))
            window.blit(text, (x + 2 + offset[0], y + 2 + offset[1]))


def main():
    #filename = "assets/pixymoon/CuteRPG_Interior/32x32/CuteRPG_Interior_custom.png"
    #filename = "assets/pixymoon/CuteRPG_Forest/32x32/CuteRPG_Forest.png"
    #filename = "assets/pixymoon/CuteRPG_Houses/32x32/CuteRPG_Houses_A-modified.png"
    filename = "assets/pixymoon/CuteRPG_Village/32x32/CuteRPG_Village.png"

    tileSize = (32, 32)
    #offset = (8, 0)
    offset = (0, 0)
    transparentColor = (0, 0, 0)

    windowSize = (1800, 1200)
    
    window = pygame.display.set_mode(windowSize)
    pygame.display.set_caption("Sprite Sheet Grid")
    clock = pygame.time.Clock()
    
    running = True
    while running:
        clock.tick(10)

        # Check for a quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the window with black
        window.fill((0, 0, 0))

        # Insert drawing code here
        # This is just a test that puts a red square in the middle of the screen
        #pygame.draw.rect(window, (255, 0, 0), (gameParams["width"] / 2 - 25, gameParams["height"] / 2 - 25, 50, 50))        
        pygame.draw.rect(window, (255, 0, 0), (windowSize[0] / 2 - 25, windowSize[1] / 2 - 25, 50, 50))

        # Display the sprite sheet
        displayGrid(filename, tileSize, offset, transparentColor, window)

        # Flip the backbuffer
        pygame.display.flip()  


# Main
if __name__ == "__main__":
    # Main function
    main()