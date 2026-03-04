import threading
import pygame
import websockets
from websockets.sync.client import connect
import json
import math

## Setting game state to 0, which means that the game is in the start menu state. 
gamestate = 0
IsConnectedInLobby = False
Rotation = 0

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
        threading.Thread(target=self.HandleBingInLobby).start()
        
    def CreateLobby(self):
        print("Creating lobby...")
        self.connection.send(json.dumps({"type": "CreateLobby", "data": {}}))
        threading.Thread(target=self.HandleBingInLobby).start()

    def StartGame(self):
        self.connection.send(json.dumps({"type": "StartGame", "data": {}}))

    @setattr
    def SendPlayerLocation(self, x, y):
        self.connection.send(json.dumps({"type": "UpdateMovementInput", "data": {"x": x, "y": y}}))

    def HandleBingInLobby(self):
        global IsConnectedInLobby
        global Rotation
        IsConnectedInLobby = True
        while IsConnectedInLobby:
            message = self.connection.recv()
            messageJSON = json.loads(message)
            if messageJSON["type"] == "GameStarted":
                print("Game started with map:", messageJSON["data"]["map"])
                self.map = messageJSON["data"]["map"]
                global gamestate
                gamestate = 4
                Rotation = math.pi / 4
                print("Starting game...")
                self.LocalPlayerLocation = {"x": 0, "y": 0}
            if gamestate == 4 and messageJSON["type"] == "UpdateLocations":
                self.Playerlocations = messageJSON["data"]["players"]
                self.LocalPlayerLocation = self.Playerlocations[self.username]
                





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
        if event.type == pygame.KEYDOWN:
            if gamestate == 4:
                if event.key == pygame.K_q:
                    Rotation -= math.pi/8
                if event.key == pygame.K_e:
                    Rotation += math.pi/8
    if gamestate == 4:
        screen.fill((0, 0, 255))
        Map = serverhandler.map
        for i in range(60):
            x,y = serverhandler.LocalPlayerLocation["x"], serverhandler.LocalPlayerLocation["y"]
            rot_i = Rotation + math.radians(i-30)
            sin = 0.02 * math.sin(rot_i)
            cos = 0.02 * math.cos(rot_i)
            for n in range(200):
                x += cos
                y += sin
                if Map[int(y)][int(x)] == 1:
                    ## Writes the lines for the walls on screan
                    pygame.draw.line(screen, (255 - n, 255 - n, 255 - n), ((screen.get_width()//60) * i, screen.get_height()//2 + (n*screen.get_height()//40)), (screen.get_width()//60*i, screen.get_height()//2 - (n*screen.get_height()//40)), 5)
                    break
                screen.get_height()//2 + sin

    pygame.display.flip()


pygame.quit()