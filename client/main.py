import threading
import pygame
import websockets
from websockets.sync.client import connect
import json

## Setting game state to 0, which means that the game is in the start menu state. 
gamestate = 0


class ServerComnicationHandler():
    print("Server Communication Handler Initialized")
    def __init__(self):
        self.connection = connect('wss://we-are-domed.onrender.com/')
        self.username = json.loads(self.connection.recv())["data"]["username"]
        print("Username received from server:", self.username)


    ##def run(self):
    ##    while True:
    ##        # Here we would handle communication with the server
    ##        pass





pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

isRunning = True

serverhandler = ServerComnicationHandler()


while isRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break

    pygame.display.flip()


pygame.quit()