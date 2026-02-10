import threading
import pygame

class ServerComnicationHandler():
    print("ServerComnicationHandler initialized")

map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1 ,1 ,1, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]



def draw_map(screen, map):
    screen.fill((0, 0, 0))

pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

isRunning = True

while isRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break

    draw_map(screen, map)
    pygame.display.flip()


pygame.quit()