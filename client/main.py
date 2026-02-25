import threading
import pygame
import websockets
from websockets.sync.client import connect
import json

## Setting game state to 0, which means that the game is in the start menu state. 
gamestate = 0
IsConnectedInLobby = False


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
        
    def CreateLobby(self):
        self.connection.send(json.dumps({"type": "CreateLobby", "data": {}}))

    def StartGame(self):
        self.connection.send(json.dumps({"type": "StartGame", "data": {}}))

    def HandleBingInLobby(self):
        global IsConnectedInLobby
        IsConnectedInLobby = True
        while IsConnectedInLobby:
            message = self.connection.recv()
            messageJSON = json.loads(message)
            if messageJSON["type"] == "GameStarted":
                print("Game started with map:", messageJSON["data"]["map"])
                self.map = messageJSON["data"]["map"]
                global gamestate
                gamestate = 4
                break
            if gamestate == 4 and messageJSON["type"] == "UpdateLocations":
                print("Received player location updates:", messageJSON["data"]["players"])
                





pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

isRunning = True

serverhandler = ServerComnicationHandler()

serverhandler.CreateLobby()
ServerComnicationHandler.StartGame(serverhandler)
while isRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break

    pygame.display.flip()


pygame.quit()