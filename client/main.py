import threading
import pygame
import websockets

## Setting game state to 0, which means that the game is in the start menu state. 
gamestate = 0


class ServerComnicationHandler():
    ##def __init__(self):
    ##    

    ##def run(self):
    ##    while True:
    ##        # Here we would handle communication with the server
    ##        pass





pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

isRunning = True

while isRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break

    pygame.display.flip()


pygame.quit()