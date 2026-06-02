## inporting needed packeges
import threading
import pygame
import websockets
from websockets.sync.client import connect
import json
import math
import time
from dataclasses import dataclass
from typing import Generic, TypeVar

## Deffining generic
T = TypeVar("T")

## Sets starting values for some global variables that are used to keep track of the game state and server connection.
## gameestate 1 means we are trying to conect to server
gamestate = 0
## We set rotaition to 0 so strait in one direction. The rotation is local and is therfor set in the client
Rotation = 0
## This is the IP adress to we are domomed servers. Curently this server is hosted on render.com. If we want to host our own server we can change this to the IP adress of our server to your we are doomed server.
ServerIP = "we-are-domed.onrender.com/"

## Created a class for the server packeges.
@dataclass(slots=True, frozen=True)
class ServerPacekt(Generic[T]):
    # A server packege is consisting of two components a type that is a string and tells us what we shold do with the packet and a data type that we cant predict that has information vital to execute the comand specefied in packet type
    type: str
    data: T

## This function makes evry text lage enuf so it fits on every screan, it takes in the text we want to render, the width of the area we want to render it in, the font name and the max font size we want to use, it then returns a font object that we can use to render the text with the correct size.
def Rezistext(text, textWidth, font_name="Arial", max_font_size=30):
    Taxtval = pygame.font.SysFont("Arial", max_font_size)
    for i in range(max_font_size):
        Taxtval = pygame.font.SysFont("Arial", max_font_size-i)
        if pygame.font.Font.size(Taxtval, text)[0] < textWidth:
            break
    return Taxtval
    
## Creates the class responsebale for comenecation betwean client and server in a good way
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
        ## This is a loop that will try to connect to the server 200 times before giving up, if it connects it will receive the username from the server and set the local player location and current movement to default values, it will also set the connected variable to true and start a new thread to handle incoming messages from the server. If it fails to connect after 200 attempts it will set the gamestate to -1 which is the connection failed state.
        ConnectionAttemt = 0
        while ConnectionAttemt < 200 and self.LeaveServer == False:
            try:
                ## We connect to the server using websockets, we use wss:// because we are using a secure connection, if we were using a non secure connection we would use ws://.
                self.connection = connect('wss://' + ServerIP)
                ## takes message frome server
                message = json.loads(self.connection.recv())
                
                ## as sonn as we connect to the server we are going to receive a message from the server that contains our username, we need this username to identify us in the game and to know which player is us when we receive updates from the server about player locations and other information.
                self.username = message["data"]["username"]
                ## Prints the username we received from the server, this is useful for debugging and to know that we have successfully connected to the server and received our username.
                print("Username received from server:", self.username)
                ## Setup veriebales with a prediction of server.
                self.LocalPlayerLocation = {"x": 0.0, "y": 0.0}
                self.CurentMovment = {"x": 0, "y": 0}
                ## Tells game that connection sucsided
                self.Connected = True
                ## Predictiing lobbys before packet arive.
                self.lobbys = []
                break
            except Exception as e:
                ConnectionAttemt += 1
        ## IF we did not connect after 200 attempts we set gamestate to -1 which is the connection failed state, this will render a screan that tells the player that we failed to connect to the server and they should try again later, this could be due to the server being down or the player having no internet connection.
        if self.connection == None:
            global gamestate
            gamestate = -1
        else:
            ## If we connected to the server we start a new thread to handle incoming messages from the server, this is important because we want to be able to receive messages from the server while still being able to render the game and respond to player input, if we did not use a separate thread for handling server messages we would not be able to do anything else while waiting for messages from the server, this way we can handle server messages in the background while still being able to render the game and respond to player input.
            threading.Thread(target=self.HandleServerConnection).start()

    ## If we have a lobby id this function will send that we want to join and if server agreas we join the new lobby
    def JoinLobbyWhitID(self,ID):
        self.connection.send(json.dumps({"type": "JoinLobby", "data": {"lobby_id": ID}}))
    
    ## Sends message to server to create a lobby
    def CreateLobby(self):
        self.connection.send(json.dumps({"type": "CreateLobby", "data": {}}))

    ## This function is called when the player clicks the leave lobby button, it sends a message to the server to leave the lobby, the server will then send a message to all players in the lobby to update the lobby information and remove the player from the lobby.
    def LeaveLobby(self):
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
        self.Enemyslocations = []
        self.Playerlocations = []
        self.lobbyID = None
        self.canStartGame = False
        self.Screnachanching = 0
        ## starts a loop that will run until the connection is closed or the player leaves the server, it will listen for messages from the server and update the game state accordingly.
        while self.connection != None and isRunning:
            ## resives a message from the server
            message = self.connection.recv()
            print(message)
            ## Mekes server messages readebale to client
            messageJSON = json.loads(message)
            Paket = ServerPacekt(type=messageJSON["type"], data=messageJSON["data"])
            ## If we leve the server we have to not recive before we close conection
            if self.LeaveServer:
                self.connection.close()
                break
            ## If server is unhappy to us for some resson it will print why
            if Paket.type == "error":
                print("Error from server:", Paket.data["message"])
            ## When we need to know what lobbys we can join this gets triggered to update that info
            if Paket.type == "AvailebaleLobbys":
                if time.time() > serverhandler.Screnachanching:
                    self.lobbys = Paket.data["lobbys"]
                    gamestate = 1
            ## When we are in a lobby this updates the information about the lobby like who is in it and if we can start the game or not and the lobby id
            if Paket.type == "LobbyInfo":
                self.players = Paket.data["Players"]
                self.lobbyID = Paket.data["lobbyID"]
                self.canStartGame = not Paket.data["gameRunning"]
                if time.time() > serverhandler.Screnachanching:
                    gamestate = 3
                    Rotation = 0
                    serverhandler.Screnachanching = 0
            ## This is a server event that means we shold prepare to start the game and load it up
            if Paket.type == "GameStarted":
                self.map = Paket.data["map"]
                gamestate = 4
                Rotation = math.pi / 4
                print("Starting game...")
                ## This is a prediction on where we are in the map. If we are wrong we are going to snap to corect positin after a while but this makes it smother
                self.LocalPlayerLocation = {"x": 10.5, "y": 10.5}
            ## Updates player locatins and also local players position, Position is used to know wher we shold render
            if Paket.type == "UpdateLocations":
                gamestate = 4
                self.Playerlocations = Paket.data["players"]
                self.Enemyslocations = Paket.data["enemyPositions"]
                for player in self.Playerlocations:
                    if player["Username"] == self.username:
                        self.LocalPlayerLocation = player["Position"]
                        break
                

            ## The server thinks you won the game and this event prints and switshes to a game scen for victory
            if Paket.type == "Winner":
                self.Screnachanching = time.time() + 10
                gamestate = 5
                print("Player won the game!")
            ## The server thinks you lost the game and this event prints and switshes to a game scen for defeat
            if Paket.type == "Caught":
                self.Screnachanching = time.time() + 10
                gamestate = -5
                print("Player lost the game!")





## starting pygame and creating the game window, this is where we will render the game and all the menus, we also set the caption of the window to "We are doomed" to make it clear that this is the game window.
pygame.init()
pygame.display.set_caption("We are doomed")
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)


## This is the main game loop, this is where we will handle all the game logic and rendering, this loop will run until the player closes the game window, we also calculate the delta time to make sure that our game runs at the same speed on all computers regardless of how fast they are.
serverhandler = None
isRunning = True
lastTime = time.time()
##ServerComnicationHandler.StartGame(serverhandler)
while isRunning:
    ## A dstep in when time.deltaTime dose not exists this calculates that.
    currentTime = time.time()
    dt = currentTime - lastTime
    lastTime = currentTime

    ## This is where we handle all the events that pygame gives us, this includes things like closing the game window, clicking buttons and resizing the game window, we also check for mouse clicks and if the player clicks on certain areas of the screen we will perform certain actions like joining a lobby or starting the game.
    for event in pygame.event.get():
        ## If we press the red X in the courner. When that happends We do a safe disconnect to not crash websocket. So the safe waits to the websocket can close closes it and then closes the game this takes 4 seconds but it is better than crashing the game and leaving the websocket open which can cause problems for the the system.
        if event.type == pygame.QUIT:
            isRunning = False
            if serverhandler != None:
                serverhandler.Disconnect()
                break
        ## This is where we handle mouse clicks, we check if the player clicks on certain areas of the screen and if they do we perform certain actions like joining a lobby or starting the game, we also check the gamestate to know what we should do when the player clicks on certain areas of the screen, for example if we are in the main menu and the player clicks on the create lobby button we will send a message to the server to create a lobby, if we are in a lobby and the player clicks on the start game button we will send a message to the server to start the game, this way we can have different buttons and actions depending on what gamestate we are in.
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            ## IF we connected wrong crash as soon as cliecked
            if gamestate == -1:
                break
            ## This is where we handle mouse clicks in the main menu, we check if the player clicks on the create lobby button, the controls button or the story button and if they do we perform the corresponding action, we also check if the player clicks on any of the lobbys that are available to join and if they do we send a message to the server to join that lobby.
            if gamestate == 1:
                if screen.get_width()//4 * 3 < mouse_pos[0] < screen.get_width() and (screen.get_height()//5)*4 < mouse_pos[1] < screen.get_height():
                    print("Create lobby button clicked")
                    serverhandler.CreateLobby()
                
                if screen.get_width()//4 * 3 < mouse_pos[0] < screen.get_width() and (screen.get_height()//5)*3 < mouse_pos[1] < (screen.get_height()//5)*4:
                    print("Controls button clicked")
                    gamestate = 6
                    
                if screen.get_width()//4 * 3 < mouse_pos[0] < screen.get_width() and (screen.get_height()//5)*2 < mouse_pos[1] < (screen.get_height()//5)*3:
                    print("Story button clicked")  
                    gamestate = 7

                for i, lobby in enumerate(serverhandler.lobbys):
                    if 0 < mouse_pos[0] < screen.get_width()//4 * 3 and 80 + i*40 < mouse_pos[1] < 100 + i*40:
                        print(f"Lobby {lobby['lobbyID']} clicked")
                        serverhandler.JoinLobbyWhitID(lobby["lobbyID"])
                        break
            ## This is where we handle mouse clicks in the lobby, we check if the player clicks on the start game button or the leave lobby button and if they do we perform the corresponding action, we also check if the player is allowed to start the game before allowing them to click the start game button, this way we can prevent players from starting the game before everyone is ready.
            if gamestate == 3:
                if serverhandler.canStartGame and 0 < mouse_pos[0] < screen.get_width()//2 and screen.get_height() - 40 < mouse_pos[1] < screen.get_height():
                    print("Start game button clicked")
                    serverhandler.StartGame()
                if screen.get_width()//2 < mouse_pos[0] < screen.get_width() and screen.get_height() - 40 < mouse_pos[1] < screen.get_height():
                    print("Leave lobby button clicked")
                    serverhandler.LeaveLobby()
            ## This is where we handle mouse clicks in the controls and story screen, we check if the player clicks on the back button and if they do we return to the main menu, this way the player can read the controls and story and then easily return to the main menu to start playing the game.
            if gamestate == 6 or gamestate == 7:
                if 0 < mouse_pos[0] < screen.get_width() and screen.get_height() - 40 < mouse_pos[1] < screen.get_height():
                    print("Back button clicked")
                    gamestate = 1
    
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
        screen.blit(pygame.font.SysFont("Arial", 30).render("We are doomed", True, (0, 0, 0)), (30, 30))
        pygame.draw.rect(screen, (0, 255, 0), (0, 70, screen.get_width()//4 * 3, screen.get_height()-70))
        for i, lobby in enumerate(serverhandler.lobbys):
            pygame.draw.rect(screen, (255, 0, 0), (0, 80 + i*40, screen.get_width()//4 * 3, 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render(str(lobby["lobbyID"]), True, (0, 0, 0)), (5, 80 + i*20))

        ## Renders the buttons for create lobby, controls and story, these buttons are on the right side of the screen and are rendered in different colors to make them easy to distinguish, we also render the text for each button on top of the button to make it clear what each button does, this way the player can easily navigate the main menu and find the options they are looking for.
        pygame.draw.rect(screen, (255, 255, 0), (screen.get_width()//4 * 3, screen.get_height()//5, screen.get_width()//4, (screen.get_height()-70) // 5))
        pygame.draw.rect(screen, (0, 122, 255), (screen.get_width()//4 * 3, (screen.get_height()//5)*3, screen.get_width()//4, (screen.get_height()) // 5))
        pygame.draw.rect(screen, (255, 0, 255), (screen.get_width()//4 * 3, (screen.get_height()//5)*4, screen.get_width()//4, (screen.get_height()) // 5))
        pygame.draw.rect(screen, (255, 127, 80), (screen.get_width()//4 * 3, (screen.get_height()//5)*2, screen.get_width()//4, (screen.get_height()) // 5))
        text = Rezistext(f"Create Lobby", screen.get_width()//4 - 20, "Arial", 30)
        text = Rezistext(f"Create Lobby", screen.get_width()//4 - 20, "Arial", 30)
        screen.blit(text.render("Create Lobby", True, (0, 0, 0)), (screen.get_width()//4 * 3 + 10, ((screen.get_height()) // 5)*4+10))
        text = Rezistext(f"Loged in as {serverhandler.username}", screen.get_width()//4 - 20, "Arial", 30)
        screen.blit(text.render(f"Loged in as {serverhandler.username}", True, (0, 0, 0)), (screen.get_width()//4 * 3 + 10, 80))
        text = Rezistext(f"Controls", screen.get_width()//4 - 20, "Arial", 30)
        screen.blit(text.render("Controls", True, (0, 0, 0)), (screen.get_width()//4 * 3 + 10, ((screen.get_height()) // 5)*3+10))
        text = Rezistext(f"Story", screen.get_width()//4 - 20, "Arial", 30)
        screen.blit(text.render("Story", True, (0, 0, 0)), (screen.get_width()//4 * 3 + 10, ((screen.get_height()) // 5)*2+10))
        pygame.display.flip()

    ## gamestate 3 is the game state when you are in a lobby waiting for the game to start.
    if gamestate == 3:
        screen.fill((0, 0, 255))
        screen.blit(pygame.font.SysFont("Arial", 30).render(f"Joined lobby: {serverhandler.lobbyID}", True, (0, 0, 0)), (5, 0))
        ## Renders all players in the lobby and marks you in yellow and others in red.
        for i, player in enumerate(serverhandler.players):
            if player["Username"] == serverhandler.username:
                pygame.draw.rect(screen, (255, 215, 0), (0, 80 + i*40, screen.get_width(), 40))
            else:
                pygame.draw.rect(screen, (255, 0, 0), (0, 80 + i*40, screen.get_width(), 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render(player["Username"], True, (0, 0, 0)), (5, 80 + i*40))
        ## IF we can start the game we render the start game button in green and if we cant start the game we render it in a darker green and change the text to game is running, this way the player can easily see if they are allowed to start the game or not and if they are not allowed to start the game they can see that the game is already running and they just have to wait for it to end before they can start a new game.
        if serverhandler.canStartGame:    
            pygame.draw.rect(screen, (0, 255, 0), (0, screen.get_height() - 40, screen.get_width()//2, 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render("Start Game", True, (0, 0, 0)), (5, screen.get_height() - 35))
        else:
            pygame.draw.rect(screen, (0, 200, 0), (0, screen.get_height() - 40, screen.get_width()//2, 40))
            screen.blit(pygame.font.SysFont("Arial", 30).render("Game is running", True, (0, 0, 0)), (5, screen.get_height() - 35))
        
        ## Renders leve lobby button.
        pygame.draw.rect(screen, (255, 0, 0), (screen.get_width()//2, screen.get_height() - 40, screen.get_width()//2, 40))
        screen.blit(pygame.font.SysFont("Arial", 30).render("Leave Lobby", True, (0, 0, 0)), (screen.get_width()//2 + 10, screen.get_height() - 35))
        pygame.display.flip()

    ## gamestate 4 is the game state the game is when you are connected and playing in a server            
    if gamestate == 4:
        ## Raycasting
        screen.fill((0, 0, 255))
        Map = serverhandler.map
        ## Loops trow 60 digreas of ratycasts
        for i in range(60):
            x,y = serverhandler.LocalPlayerLocation["x"], serverhandler.LocalPlayerLocation["y"]
            rot_i = Rotation + math.radians(i-30)
            ## calculates the sin and cos of the rotation of the ray, this is used to move the ray forward in the correct direction, we multiply by 0.01 to make the ray move in small increments, this way we can check for collisions with walls and players more accurately, if we moved the ray in larger increments we might skip over walls and players and not detect them correctly.
            sin = 0.01 * math.sin(rot_i)
            cos = 0.01 * math.cos(rot_i)
            ## This is where we keep track of players and enemys in sight, we need to keep track of them in case we hit a wall and need to render them before the wall, if we did not keep track of them we would not be able to render them correctly and they would appear to be behind the wall even if they are in front of it, this way we can render them in the correct order and make sure that they appear in front of the wall if they are in front of it and behind the wall if they are behind it.
            player_in_sight = []
            Enemys_in_sight = []
            ## Shoots ray 500 uniits forward
            for n in range(500):
                x += cos
                y += sin

                ## Added player detection, if a player is in sight it will add it to the player_in_sight list with the distance to the player.
                for player in serverhandler.Playerlocations:
                    if player["Username"] != serverhandler.username and int(player["Position"]["x"]*30) == int(x*30) and int(player["Position"]["y"]*30) == int(y*30):
                        player_in_sight.append({"Player": player, "dist": n * 0.05 * math.cos(math.radians(i-30)), "raytravle": n})

                ## Cheking for enemys in sight, this is basicly the same as player detection but for enemys, it adds enemys in sight to the Enemys_in_sight list with the distance to the enemy.
                for enemy in serverhandler.Enemyslocations:
                    if int(enemy["x"]*30) == int(x*30) and int(enemy["y"]*30) == int(y*30):
                        Enemys_in_sight.append({"Enemy": enemy, "dist": n * 0.05 * math.cos(math.radians(i-30)), "raytravle": n})


                screenwidth = screen.get_width()
                ## render somthing as big as a wall if the ray hits a wall, the size of the wall is determined by the distance to the wall, and also makes it darker the further away it is.
                if Map[int(y)][int(x)] == 1 or Map[int(y)][int(x)] == 2:
                    dist = n * 0.05 * math.cos(math.radians(i-30))
                    Column_height = (screen.get_height() / (dist + 0.000001))/2
                    ## Writes the lines for the walls on screan
                    ## value 1 means wall, value 2 means goal, the goal is rendered in a different color to make it easier to see.
                    if Map[int(y)][int(x)] == 1:
                        pygame.draw.line(screen, ((max(0, int(255-n)), max(0,int(255-n)),0)), (screen.get_width()//60*i, screen.get_height()//2+Column_height), (screen.get_width()//60*i, screen.get_height()//2-Column_height),screenwidth//60)
                    elif Map[int(y)][int(x)] == 2:
                        pygame.draw.line(screen, (0,0,0), (screen.get_width()//60*i, screen.get_height()//2+Column_height), (screen.get_width()//60*i, screen.get_height()//2-Column_height),screenwidth//60)
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
            ## renders enemys in sight, the distance is used to make the enemy smaller the further away they are, and also to make them darker the further away they are, enemys are rendered in red to make them easy to distinguish from players.
            for enemyInfo in Enemys_in_sight:
                dist = enemyInfo["dist"]
                Column_height = (screen.get_height() / (dist + 0.000001)) / 2
                enemy_body_scale = 0.4
                enemy_head_scale = 0.3
                y_floor = screen.get_height() // 2 + Column_height
                y_body_top = y_floor - (Column_height * 2 * enemy_body_scale)
                y_head_top = y_body_top - (Column_height * enemy_head_scale)
                pygame.draw.line(screen, (max(0,int(255 - enemyInfo["raytravle"])), max(0,int(255 - enemyInfo["raytravle"])), max(0,int(255 - enemyInfo["raytravle"]))), (screen.get_width() // 60 * i, y_body_top+1), (screen.get_width() // 60 * i, y_head_top), screenwidth // 60)    

        ## Movment logic

        ## Presed is a list of pressed buttons in this frame
        pressed = pygame.key.get_pressed()
        movebuttons = 0
        forwardMovmentX = 0
        forwardMovmentY = 0
        if pressed[pygame.K_w]:
            ## calculade forward movment in the direction we are facing, we use the rotation to calculate the direction we are facing and then multiply it by the movment speed to get the amount we should move in that direction, this way we can move in the direction we are facing and not just in the cardinal directions, this makes the movement more fluid and allows for more precise control.
            dirx = math.cos(Rotation) * 1
            diry = math.sin(Rotation) * 1
            forwardMovmentX = dirx * 1
            forwardMovmentY = diry * 1
            movebuttons += 1
        elif pressed[pygame.K_s]:
            ## calculade backward movment in the direction we are facing, this is the same as forward movment but we multiply by -1 to move in the opposite direction, this way we can move backwards in the direction we are facing and not just in the cardinal directions, this makes the movement more fluid and allows for more precise control.
            dirx = math.cos(Rotation) * 1
            diry = math.sin(Rotation) * 1
            forwardMovmentX = dirx * -1
            forwardMovmentY = diry * -1
            movebuttons += 1

        ## If nesesary send movment input to server, if we are pressing a move button we send the movment input to the server, if we are not pressing any move buttons we send 0,0 to the server to indicate that we are not moving, this way the server can update our position correctly and we can have smooth movement in the game, if we did not send 0,0 when we are not moving the server would not know that we stopped moving and our character would keep moving in the last direction we were moving in, this way we can have more precise control over our character and make sure that it stops when we want it to stop.
        if movebuttons != 0:
            serverhandler.updateMovmentInput(forwardMovmentX, forwardMovmentY)
        else:
            serverhandler.updateMovmentInput(0, 0)

        ## Loking around logic 
        if pressed[pygame.K_d]:
            Rotation += (math.pi/800) * dt * 500
        elif pressed[pygame.K_a]:
            Rotation -= (math.pi/800) * dt * 500
        
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

    ## gamestate 6 is the controls screen, this screen shows the controls for the game and how to navigate the menus, this way the player can easily learn how to play the game and navigate the menus without having to guess or look up the controls online, we also render a back button that allows the player to return to the main menu when they are done reading the controls, this way they can easily return to the main menu and start playing the game when they are ready.
    if gamestate == 6:
        serverhandler.Screnachanching = time.time() + 1
        screen.fill((0, 255, 0))
        Conntrolstext = ["W - Move forward", "S - Move backward", "A - Turn left", "D - Turn right","---------------------","Navigate in menus with the mouse", "To close game pres the x in the corner"]
        for i,v in enumerate(Conntrolstext):
            text = Rezistext(v, screen.get_width() - 20, "Arial", 30)
            screen.blit(text.render(v, True, (0, 0, 0)), (10, (i*30+20)))
        pygame.draw.rect(screen, (255, 0, 0), (0, screen.get_height() - 40, screen.get_width(), 40))
        screen.blit(pygame.font.SysFont("Arial", 30).render("Back", True, (0, 0, 0)), (5, screen.get_height() - 35))
        pygame.display.flip()
    
    ## gamestate 7 is the story screen, this screen shows the story of the game and the objective of the game, this way the player can understand the context of the game and what they are trying to accomplish, we also render a back button that allows the player to return to the main menu when they are done reading the story, this way they can easily return to the main menu and start playing the game when they are ready. The story is rendered in multiple lines to make it easier to read and to fit on the screen, we also use a different color for the text to make it stand out from the background and make it easier to read.
    if gamestate == 7:
        serverhandler.Screnachanching = time.time() + 1
        screen.fill((0, 255, 0))
        Storytext = ["You have just turned off an evil AI.", "But when you did you discovered", "that it was a timer on shutdown.", "The AI have deployed evil drones", "to kill you before the shutdown.", "You have to escape before the drones arrive.", "Find the black exit and go into it.", "Then you win and have shutdown the AI."]
        for i,v in enumerate(Storytext):
            text = Rezistext(v, screen.get_width() - 20, "Arial", 30)
            screen.blit(text.render(v, True, (0, 0, 0)), (10, (i*30+20)))
        pygame.draw.rect(screen, (255, 0, 0), (0, screen.get_height() - 40, screen.get_width(), 40))
        screen.blit(pygame.font.SysFont("Arial", 30).render("Back", True, (0, 0, 0)), (5, screen.get_height() - 35))
        pygame.display.flip()

        
    ## update frame
    pygame.display.flip()


## when we get out of loop we turn of the game.
pygame.quit()