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
        ConnectionAttemt = 0
        while ConnectionAttemt < 5:
            try:
                self.connection = connect('wss://we-are-domed.onrender.com/')
                self.username = json.loads(self.connection.recv())["data"]["username"]
                print("Username received from server:", self.username)
                break
            except TimeoutError:
                ConnectionAttemt += 1

    def JoinLobbyWhitID(self,ID):
        self.connection.send(json.dumps({"type": "join", "data": {"lobby_id": ID}}))
        





pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

isRunning = True

serverhandler = ServerComnicationHandler()

serverhandler.JoinLobbyWhitID(1)
while isRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break

    pygame.display.flip()


pygame.quit()