import threading
import pygame
import websockets
from websockets.sync.client import connect
import json
import math

## Setting game state to 0, which means that the game is in the start menu state. 
gamestate = 0
Rotation = 0
ServerIP = "we-are-domed.onrender.com/"

class ServerComnicationHandler():
    print("Server Communication Handler Initialized")
    def __init__(self):
        self.Connected = False
        self.connection = None
        self.LeaveServer = False
        threading.Thread(target=self.ConnectToServer).start()

    def ConnectToServer(self):
        ConnectionAttemt = 0
        while ConnectionAttemt < 200 and self.LeaveServer == False:
            try:
                self.connection = connect('wss://' + ServerIP)
                self.username = json.loads(self.connection.recv())["data"]["username"]
                print("Username received from server:", self.username)
                self.LocalPlayerLocation = {"x": 5, "y": 5}
                self.CurentMovment = {"x": 0, "y": 0}
                self.Connected = True
                break
            except Exception as e:
                ConnectionAttemt += 1
        if self.connection == None:
            global gamestate
            gamestate = -1
        
        threading.Thread(target=self.HandleServerConnection).start()

    def JoinLobbyWhitID(self,ID):
        self.connection.send(json.dumps({"type": "JoinLobby", "data": {"lobby_id": ID}}))
        
    def CreateLobby(self):
        print("Creating lobby...")
        self.connection.send(json.dumps({"type": "CreateLobby", "data": {}}))

    def StartGame(self):
        self.connection.send(json.dumps({"type": "StartGame", "data": {}}))
    
    def Disconnect(self):
        self.LeaveServer = True

    def updateMovmentInput(self, x, y):
        if self.CurentMovment != {"x": x, "y": y}:
            self.connection.send(json.dumps({"type": "UpdateMovementInput", "data": {"x": x, "y": y}}))
            self.CurentMovment = {"x": x,"y": y}

    def HandleServerConnection(self):
        global gamestate
        global Rotation
        self.lobbys = []
        self.players = []
        self.lobbyID = None
        while self.connection != None and isRunning:
            message = self.connection.recv()
            messageJSON = json.loads(message)
            if self.LeaveServer:
                self.connection.close()
                break
            if messageJSON["type"] == "error":
                print("Error from server:", messageJSON["data"]["message"])
            if gamestate == 1 and messageJSON["type"] == "AvailebaleLobbys":
                self.lobbys = messageJSON["data"]["lobbys"]
            if messageJSON["type"] == "LobbyInfo":
                self.players = messageJSON["data"]["Players"]
                self.lobbyID = messageJSON["data"]["lobbyID"]
                gamestate = 3
            if gamestate == 3 and messageJSON["type"] == "GameStarted":
                print("Game started with map:", messageJSON["data"]["map"])
                self.map = messageJSON["data"]["map"]
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
                

        






pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

serverhandler = None
isRunning = True

##ServerComnicationHandler.StartGame(serverhandler)
while isRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            if serverhandler != None:
                serverhandler.Disconnect()
                break
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if gamestate != 4:
                print("Mouse clicked at:", mouse_pos)
            if gamestate == -1:
                break
            if gamestate == 1:
                if screen.get_width()//4 * 3 < mouse_pos[0] < screen.get_width() and (screen.get_height()+70) // 2 < mouse_pos[1] < screen.get_height():
                    print("Create lobby button clicked")
                    serverhandler.CreateLobby()
                
                for i, lobby in enumerate(serverhandler.lobbys):
                    if 0 < mouse_pos[0] < screen.get_width()//4 * 3 and 80 + i*40 < mouse_pos[1] < 100 + i*40:
                        print(f"Lobby {lobby['lobbyID']} clicked")
                        serverhandler.JoinLobbyWhitID(lobby["lobbyID"])
                        break
            if gamestate == 3:
                if 0 < mouse_pos[0] < screen.get_width()//2 and screen.get_height() - 40 < mouse_pos[1] < screen.get_height():
                    print("Start game button clicked")
                    serverhandler.StartGame()
                if screen.get_width()//2 < mouse_pos[0] < screen.get_width() and screen.get_height() - 40 < mouse_pos[1] < screen.get_height():
                    print("Leave lobby button clicked")
    
    ## gamestate 1 Not Yet Connected to a server, but trying to connect.
    if gamestate == 0:
        screen.fill((0, 255, 0))
        screen.blit(pygame.font.SysFont("Arial", 30).render("Connecting to server...", True, (0, 0, 0)), (screen.get_width() // 2 - 125, screen.get_height() // 2 - 15))
        pygame.display.flip()
        if serverhandler == None:
            serverhandler = ServerComnicationHandler()
        if serverhandler.Connected:
            gamestate = 1

    ## Connection Faild for some reason, could be server down or no internet connection.
    if gamestate == -1:
        screen.fill((255, 0, 0))
        screen.blit(pygame.font.SysFont("Arial", 30).render("Failed to connect to server.", True, (0, 0, 0)), (screen.get_width() // 2 - 125, screen.get_height() // 2 - 15))
        pygame.display.flip()

    ## Connected but not in a lobby or started game yet.
    if gamestate == 1:
        screen.fill((255, 255, 0))
        screen.blit(pygame.font.SysFont("Arial", 30).render(f"Loged in as {serverhandler.username}", True, (0, 0, 0)), (30, 30))
        pygame.draw.rect(screen, (0, 255, 0), (0, 70, screen.get_width()//4 * 3, screen.get_height()-70))
        for i, lobby in enumerate(serverhandler.lobbys):
            pygame.draw.rect(screen, (255, 0, 0), (0, 80 + i*40, screen.get_width()//4 * 3, 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render(str(lobby["lobbyID"]), True, (0, 0, 0)), (5, 80 + i*20))

        pygame.draw.rect(screen, (0, 0, 255), (screen.get_width()//4 * 3, 70, screen.get_width()//4, (screen.get_height()-70) // 2))
        pygame.draw.rect(screen, (255, 0, 255), (screen.get_width()//4 * 3, (screen.get_height()+70) // 2, screen.get_width()//4, (screen.get_height()-70) // 2))
        text = pygame.font.SysFont("Arial", 30)
        for i in range(30):
            text = pygame.font.SysFont("Arial", 30-i)
            if pygame.font.Font.size(text,"Create Lobby")[0] < screen.get_width()//4 - 20:
                break
        screen.blit(text.render("Create Lobby", True, (0, 0, 0)), (screen.get_width()//4 * 3 + 10, (screen.get_height()+70) // 2))
        pygame.display.flip()

    ## gamestate 3 is the game state when you are in a lobby waiting for the game to start.
    if gamestate == 3:
        screen.fill((0, 0, 255))
        screen.blit(pygame.font.SysFont("Arial", 30).render(f"Joined lobby: {serverhandler.lobbyID}", True, (0, 0, 0)), (5, 0))
        for i, player in enumerate(serverhandler.players):
            if player["Username"] == serverhandler.username:
                pygame.draw.rect(screen, (255, 215, 0), (0, 80 + i*40, screen.get_width(), 40))
            else:
                pygame.draw.rect(screen, (255, 0, 0), (0, 80 + i*40, screen.get_width(), 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render(player["Username"], True, (0, 0, 0)), (5, 80 + i*40))
        pygame.draw.rect(screen, (0, 255, 0), (0, screen.get_height() - 40, screen.get_width()//2, 40))
        screen.blit(pygame.font.SysFont("Arial", 30).render("Start Game", True, (0, 0, 0)), (5, screen.get_height() - 35))
        pygame.draw.rect(screen, (255, 0, 0), (screen.get_width()//2, screen.get_height() - 40, screen.get_width()//2, 40))
        screen.blit(pygame.font.SysFont("Arial", 30).render("Leave Lobby", True, (0, 0, 0)), (screen.get_width()//2 + 10, screen.get_height() - 35))
        pygame.display.flip()

    ## gamestate 4 is the game state the game is when you are connected and playing in a server            
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