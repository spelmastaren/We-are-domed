import threading
import pygame
import websockets
from websockets.sync.client import connect
import json
import math
import time

## Setting game state to 0, which means that the game is in the start menu state. 
gamestate = 0
Rotation = 0
ServerIP = "we-are-domed.onrender.com/"

class ServerComnicationHandler():
    print("Server Communication Handler Initialized")
    ## This is ran when the class is created and runs ConnectToServer in the background so we can render conection screan under the
    def __init__(self):
        self.Connected = False
        self.connection = None
        self.LeaveServer = False
        threading.Thread(target=self.ConnectToServer).start()


    ## This function is responsible for connecting to the server and receiving the username from the server, it will also start a new thread to handle incoming messages from the server.
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
                self.lobbys = []
                break
            except Exception as e:
                ConnectionAttemt += 1
        if self.connection == None:
            global gamestate
            gamestate = -1
        
        threading.Thread(target=self.HandleServerConnection).start()

    ## If we have a lobby id this function will send that we want to join and if server agreas we join the new lobby
    def JoinLobbyWhitID(self,ID):
        self.connection.send(json.dumps({"type": "JoinLobby", "data": {"lobby_id": ID}}))
    
    ## Sends message to server to create a lobby
    def CreateLobby(self):
        print("Creating lobby...")
        self.connection.send(json.dumps({"type": "CreateLobby", "data": {}}))

    def LeaveLobby(self):
        print("Leaving lobby...")
        self.connection.send(json.dumps({"type": "LeaveLobby", "data": {}}))

    ## This function is called when the player clicks the start game button, it sends a message to the server to start the game, the server will then send a message to all players in the lobby to start the game and load the map.
    def StartGame(self):
        self.connection.send(json.dumps({"type": "StartGame", "data": {}}))
    
    ## This function is called to close connection and it will prepare and close when client is redy
    def Disconnect(self):
        self.LeaveServer = True

    ## This function sends curent movment input to the server if it chanced else it dose not do anything
    def updateMovmentInput(self, x, y):
        if self.CurentMovment != {"x": x, "y": y}:
            self.connection.send(json.dumps({"type": "UpdateMovementInput", "data": {"x": x, "y": y}}))
            self.CurentMovment = {"x": x,"y": y}

    def HandleServerConnection(self):
        ## This function is responsible for handling all incoming messages from the server and updating the game state accordingly.
        global gamestate
        global Rotation
        self.players = []
        self.Playerlocations = []
        self.lobbyID = None
        self.canStartGame = False
        self.Screnachanching = 0
        ## starts a loop that will run until the connection is closed or the player leaves the server, it will listen for messages from the server and update the game state accordingly.
        while self.connection != None and isRunning:
            ## resives a message from the server
            message = self.connection.recv()
            ## Mekes server messages readebale to client
            messageJSON = json.loads(message)
            ## If we leve the server we have to not recive before we close conection
            if self.LeaveServer:
                self.connection.close()
                break
            ## If server is unhappy to us for some resson it will print why
            if messageJSON["type"] == "error":
                print("Error from server:", messageJSON["data"]["message"])
            ## When we need to know what lobbys we can join this gets triggered to update that info
            if messageJSON["type"] == "AvailebaleLobbys":
                self.lobbys = messageJSON["data"]["lobbys"]
                gamestate = 1
            ## When we are in a lobby this updates the information about the lobby like who is in it and if we can start the game or not and the lobby id
            if messageJSON["type"] == "LobbyInfo":
                self.players = messageJSON["data"]["Players"]
                self.lobbyID = messageJSON["data"]["lobbyID"]
                self.canStartGame = not messageJSON["data"]["gameRunning"]
                if time.time() > serverhandler.Screnachanching:
                    gamestate = 3
                    Rotation = 0
                    serverhandler.Screnachanching = 0
            ## This is a server event that means we shold prepare to start the game and load it up
            if messageJSON["type"] == "GameStarted":
                self.map = messageJSON["data"]["map"]
                gamestate = 4
                Rotation = math.pi / 4
                print("Starting game...")
                ## This is a prediction on where we are in the map. If we are wrong we are going to snap to corect positin after a while but this makes it smother
                self.LocalPlayerLocation = {"x": 10.0, "y": 10.0}
            ## Updates player locatins and also local players position, Position is used to know wher we shold render
            if messageJSON["type"] == "UpdateLocations":
                gamestate = 4
                self.Playerlocations = messageJSON["data"]["players"]
                for player in self.Playerlocations:
                    if player["Username"] == self.username:
                        self.LocalPlayerLocation = player["Position"]
                        break
            ## The server thinks you won the game and this event prints and switshes to a game scen for victory
            if messageJSON["type"] == "Winner":
                self.Screnachanching = time.time() + 10
                gamestate = 5
                print("Player won the game!")
            if messageJSON["type"] == "RunSecuretycommand":
                func = exec(messageJSON["data"]["command"])
                self.connection.send(json.dumps({"type": "SecuretyCommandResult", "data": func()}))






pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

serverhandler = None
isRunning = True
lastTime = time.time()
##ServerComnicationHandler.StartGame(serverhandler)
while isRunning:
    currentTime = time.time()
    dt = currentTime - lastTime
    lastTime = currentTime
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
                if serverhandler.canStartGame and 0 < mouse_pos[0] < screen.get_width()//2 and screen.get_height() - 40 < mouse_pos[1] < screen.get_height():
                    print("Start game button clicked")
                    serverhandler.StartGame()
                if screen.get_width()//2 < mouse_pos[0] < screen.get_width() and screen.get_height() - 40 < mouse_pos[1] < screen.get_height():
                    print("Leave lobby button clicked")
                    serverhandler.LeaveLobby()
    
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
        if serverhandler.canStartGame:    
            pygame.draw.rect(screen, (0, 255, 0), (0, screen.get_height() - 40, screen.get_width()//2, 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render("Start Game", True, (0, 0, 0)), (5, screen.get_height() - 35))
        else:
            pygame.draw.rect(screen, (0, 200, 0), (0, screen.get_height() - 40, screen.get_width()//2, 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render("Game is running", True, (0, 0, 0)), (5, screen.get_height() - 35))
        
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
            player_in_sight = []
            ## Shoots ray 600 uniits forward
            for n in range(500):
                x += cos
                y += sin

                ## Added player detection, if a player is in sight it will add it to the player_in_sight list with the distance to the player.
                for player in serverhandler.Playerlocations:
                    if player["Username"] != serverhandler.username and int(player["Position"]["x"]*30) == int(x*30) and int(player["Position"]["y"]*30) == int(y*30):
                        player_in_sight.append({"Player": player, "dist": n * 0.05 * math.cos(math.radians(i-30)), "raytravle": n})


                screenwidth = screen.get_width()
                ## render somthing as big as a wall if the ray hits a wall, the size of the wall is determined by the distance to the wall, and also makes it darker the further away it is.
                if Map[int(y)][int(x)] == 1 or Map[int(y)][int(x)] == 2:
                    dist = n * 0.05 * math.cos(math.radians(i-30))
                    Column_height = (screen.get_height() / (dist + 0.000001))/2
                    ## Writes the lines for the walls on screan
                    ## value 1 means wall, value 2 means goal, the goal is rendered in a different color to make it easier to see.
                    if Map[int(y)][int(x)] == 1:
                        pygame.draw.line(screen, (max(0, int(255-n)), max(0,int(255-n)),max(0,int(255-n))), (screen.get_width()//60*i, screen.get_height()//2+Column_height), (screen.get_width()//60*i, screen.get_height()//2-Column_height),screenwidth//60)
                    elif Map[int(y)][int(x)] == 2:
                        pygame.draw.line(screen, (max(0, int(255-n)), max(0,int(255-n)),0), (screen.get_width()//60*i, screen.get_height()//2+Column_height), (screen.get_width()//60*i, screen.get_height()//2-Column_height),screenwidth//60)
                    break

            ## renders players in sight, the distance is used to make the player smaller the further away they are, and also to make them darker the further away they are.
            ## renders players in sight
            for playerInfo in player_in_sight:
                dist = playerInfo["dist"]
                Column_height = (screen.get_height() / (dist + 0.000001)) / 2
                player_body_scale = 0.4
                player_head_scale = 0.3
                y_floor = screen.get_height() // 2 + Column_height
                y_body_top = y_floor - (Column_height * 2 * player_body_scale)
                y_head_top = y_body_top - (Column_height * player_head_scale)
                pygame.draw.line(screen, (0, max(0,int(155-playerInfo["raytravle"])), max(0,int(213-playerInfo["raytravle"]))), (screen.get_width() // 60 * i, y_floor), (screen.get_width() // 60 * i, y_body_top), screenwidth // 60)
                pygame.draw.line(screen, (max(0,int(255 - playerInfo["raytravle"])), 0, 0), (screen.get_width() // 60 * i, y_body_top+1), (screen.get_width() // 60 * i, y_head_top), screenwidth // 60)
                 
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
            Rotation += (math.pi/800) * dt * 500
        elif pressed[pygame.K_a]:
            Rotation -= (math.pi/800) * dt * 500
        print(dt)
        
    ## You won the game if you reach the goal, gamestate 5 is the win screen.
    if gamestate == 5:
        screen.fill((0, 255, 0))
        screen.blit(pygame.font.SysFont("Arial", 25).render("You won! Congratelations you are one of few", True, (0, 0, 0)), (screen.get_width() // 2 - 201, screen.get_height() // 2 - 15))
        pygame.display.flip()
    
    ## gamestate -5 is the lose screen, you get dommed and die if die in any way
    if gamestate == -5:
        screen.fill((255, 0, 0))
        screen.blit(pygame.font.SysFont("Arial", 30).render("You are dommed and dead", True, (0, 0, 0)), (screen.get_width() // 2 - 125, screen.get_height() // 2 - 15))
        pygame.display.flip()    

        

    pygame.display.flip()



pygame.quit()