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
ServerIP = "we-are-domed.onrender.com/"

class ServerComnicationHandler():
    print("Server Communication Handler Initialized")
    def __init__(self):
        ConnectionAttemt = 0
        while ConnectionAttemt < 200:
            try:
                print('wss://' + ServerIP)
                self.connection = connect('wss://' + ServerIP)
                self.username = json.loads(self.connection.recv())["data"]["username"]
                print("Username received from server:", self.username)
                self.LocalPlayerLocation = {"x": 5, "y": 5}
                self.CurentMovment = {"x": 0, "y": 0}
                break
            except TimeoutError:
                print("Connection attempt failed, retrying...")
                ConnectionAttemt += 1
        if self.connection == None:
            Exception(TimeoutError) 

    def JoinLobbyWhitID(self,ID):
        self.connection.send(json.dumps({"type": "join", "data": {"lobby_id": ID}}))
        threading.Thread(target=self.HandleBingInLobby).start()
        
    def CreateLobby(self):
        print("Creating lobby...")
        self.connection.send(json.dumps({"type": "CreateLobby", "data": {}}))
        threading.Thread(target=self.HandleBingInLobby).start()

    def StartGame(self):
        self.connection.send(json.dumps({"type": "StartGame", "data": {}}))

    def updateMovmentInput(self, x, y):
        if self.CurentMovment != {"x": x, "y": y}:
            self.connection.send(json.dumps({"type": "UpdateMovementInput", "data": {"x": x, "y": y}}))
            self.CurentMovment = {"x": x,"y": y}

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
                self.LocalPlayerLocation = {"x": 10.0, "y": 10.0}
            if gamestate == 4 and messageJSON["type"] == "UpdateLocations":
                self.Playerlocations = messageJSON["data"]
                for player in self.Playerlocations["players"]:
                    if player["Username"] == self.username:
                        self.LocalPlayerLocation = player["Position"]
                        break
                print("Player locations updated:", self.Playerlocations)
                

        






pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

isRunning = True

serverhandler = ServerComnicationHandler()

serverhandler.CreateLobby()

##ServerComnicationHandler.StartGame(serverhandler)
while isRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break
                
    if gamestate == 4:
        ## Raycasting
        screen.fill((0, 0, 255))
        Map = serverhandler.map
        for i in range(60):
            x,y = serverhandler.LocalPlayerLocation["x"], serverhandler.LocalPlayerLocation["y"]
            rot_i = Rotation + math.radians(i-30)
            sin = 0.01 * math.sin(rot_i)
            cos = 0.01 * math.cos(rot_i)
            for n in range(200):
                x += cos
                y += sin
                screenwidth = screen.get_width()
                if Map[int(y)][int(x)] == 1:
                    dist = n * 0.05 * math.cos(math.radians(i-30))
                    Column_height = (screen.get_height() / (dist + 0.000001))/2
                    ## Writes the lines for the walls on screan
                    pygame.draw.line(screen, (255-n, 255-n,255-n), (screen.get_width()//60*i, screen.get_height()//2+Column_height), (screen.get_width()//60*i, screen.get_height()//2-Column_height),screenwidth//60)
                    break
        ## Movment logic
        pressed = pygame.key.get_pressed()
        movebuttons = 0
        forwardMovmentX = 0
        forwardMovmentY = 0
        if pressed[pygame.K_w]:
            dirx = math.cos(Rotation) * 1
            diry = math.sin(Rotation) * 1
            forwardMovmentX = dirx * 1
            forwardMovmentY = diry * 1
            movebuttons += 1
        elif pressed[pygame.K_s]:
            dirx = math.cos(Rotation) * 1
            diry = math.sin(Rotation) * 1
            forwardMovmentX = dirx * -1
            forwardMovmentY = diry * -1
            movebuttons += 1

        if movebuttons != 0:
            serverhandler.updateMovmentInput(forwardMovmentX, forwardMovmentY)
        else:
            serverhandler.updateMovmentInput(0, 0)

        ## Loking around logic 
        if pressed[pygame.K_d]:
            Rotation += math.pi/800
        elif pressed[pygame.K_a]:
            Rotation -= math.pi/800

    pygame.display.flip()



pygame.quit()