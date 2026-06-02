// prints Server initialized so i know code started corectly
console.log("Server initialized");

// gets websocket packege and creates a websocket server on port 8080
const ws = require("ws");
const wss = new ws.Server({ port: 8080 });

// Sets every players spead to 0.05 units per server tick.
const PlayerSpeed = 0.05;

// A number that keeps count and is assigned to player so no player gets same username as someone else.
let playerjoinnumber = 1;

// Serverr ID adding is used so 2 servers never get the same lobby ID, this is important because lobby ID is used to identify lobbys and if 2 lobbys have the same ID it can cause problems when players try to join lobbys or when the server tries to update the game state of a lobby, this way we can ensure that every lobby has a unique ID and we can easily identify and manage lobbys on the server.
let serverIDadding = 1;

// creates maps so we can identefy players and lobbys by lobby id and websocket connection.
let lobbys = new Map();
let players = new Map();

// Creates lobby class so multebale of the object can be created and used.
class lobby {
    // When this is constructed we create all varibales we are going to use in lobby but we set them to the ovies awnser or nothing.
    constructor(name) {
        this.map = null;
        this.ID = name;
        this.players = [];
        this.open = true;
        this.Interval = null;
        this.sholdChekIfendGame = false;
        this.enemies = [];
        console.log("Lobby created with ID:", name);
    };

    // This function is called to prepare the lobby for a new game, it resets all players in the lobby to their starting position and state, it also generates a new map for the lobby and spawns enemies in the lobby, this way we can ensure that every game in the lobby is different and that players have a new experience every time they play, it also makes sure that all players are reset and ready for the new game so we can have a smooth transition between games and avoid any issues with players being in the wrong state or position when a new game starts.
    PerpareLobby() {
        // resers every player in the lobby to starting position and state
        for (const player of this.players) {
            player.position = { x: 10.5, y: 10.5 };
            player.currentInput = { x: 0, y: 0};
            player.InGame = false;
        };
        // prints out that players are done
        console.log("Lobby with ID:", this.ID, " have all players reset and redy");
        // Uses A* to get the way frome start to goal. This is to see if map is playebale and fun.
        let [map, goal] = randomizemap();
        while (FindshortestPath(map, { x: 10, y: 10 }, { x: goal.x, y: goal.y }) == null) {
            [map, goal] = randomizemap();
        };
        // make starting tile always be a air tile so player dose not spawn in a wall.
        map[10][10] = 0;
        // Print Lobby Map Prepared with ID: lobby ID and goal at:, goal position
        console.log("Lobby Map Prepared with ID:", this.ID, "and goal at:", goal);
        // set it as the lobby map
        this.map = map;
        // start enemy list as emty and add enemys to lobby.
        this.enemies = [];
        // Spawn Enemies
        let Enemy = null;
        // Get 10 ennemys to spawn in air tiles and not on the player spawn tile.
        for (let i = 0; i < 10; i++) {
            while (true) {
                const spawn = { x: Math.floor(Math.random() * 100), y: Math.floor(Math.random() * 100) };
                if (this.map[Math.floor(spawn.y)][Math.floor(spawn.x)] === 0 && (spawn.x !== 10 || spawn.y !== 10)) {
                    Enemy = new enemy(this, { x: spawn.x + 0.5, y: spawn.y + 0.5 });
                    break;
                }
            }
            // add the enemy to the lobby enemys list
            this.enemies.push(Enemy);
        }
        // Lobby is now prepaired and we have spawned ennemys, print that out with lobby ID.
        console.log("Lobby with ID:", this.ID, " have enemies spawned redy and hungry for players to hunt");
    }

    // Stats the game
    startGame() {
        // Sends out a start packet to all players in lobby with the map data so they can start the game, it also sets all players in the lobby to in game and resets their movement input so they start with no movement, this way we can ensure that all players are in the correct state and have the correct information to start the game, it also makes sure that all players are ready and that the game starts smoothly without any issues with players being in the wrong state or having the wrong information when the game starts.
        // lopps trow all players in lobby
        for (const player of this.players) {
            player.InGame = true;
            player.HasMovedInCurrentGame = false;
            // if connection is open send start game packet with map data else close connection
            if (player.conection.readyState === ws.OPEN) {
                player.conection.send(JSON.stringify({ type: "GameStarted", data: { map: this.map } }));
            } else {
                // if connection is not open log that player connection is missed and close connection 
                player.conection.close();
            }
        }
        // Sets game loops every AI gets its own loop.
        this.Interval = setInterval(() => this.GameUpdate(), 50);
        // loop trow all enemys in lobby and set interval for them to update every 50 ms
        for (const Enemy of this.enemies) {
            Enemy.Interval = setInterval(() => Enemy.GameUpdate(), 150);
        }
    }

    GameUpdate() {
        // makes a list with all player names and positions
        let playerInfos = [];
        // loop trow all players in lobby and update their position based on their movement input and check if they have reached the goal or if they have been caught by an enemy, if they have reached the goal send them a winner packet and if they have been caught send them a caught packet, this way we can ensure that players are updated correctly and that the game state is accurate, it also makes sure that players are notified of important events like winning or being caught so they can react accordingly and have a better gaming experience.
        for (const player of this.players) {
            // if player is not in current game skip them and do not update their position or check for win or lose conditions
            if (player.InGame === true) {
                    // cheks if player is on the goal tile
                    if (this.map[Math.floor(player.position.y)][Math.floor(player.position.x)] === 2) {
                        // in that case make the player shold get a win screan so we can tell that to the players client and remember player is no longer in game
                        player.InGame = false;
                        // Prints out that player has won the game in lobby with ID: lobby ID and player username, this is for debugging and to have a log of who wins games and to make sure that the win condition is working correctly, it also makes it more fun to see who wins games and to have a record of it on the server.
                        console.log("Player", player.Username, "has reached the goal and won the game!");
                        // Tells the players client that player won
                        player.conection.send(JSON.stringify({ type: "Winner", data: {} }));
                        // Becuse we have less players we need to chek if we shold stop the current match.
                        this.sholdChekIfendGame = true;
                    }

                    // Cheks if player position is on the same as an enemy position, if they are then player is caught and we need to send them a caught packet and make them no longer in game, this way we can ensure that the lose condition is working correctly and that players are notified when they are caught by an enemy so they can react accordingly and have a better gaming experience, it also makes the game more fun and challenging to have enemies that can catch players and make them lose the game.
                    for (const enemy of this.enemies) { 
                        if (Math.floor(enemy.position.x * 10) === Math.floor(player.position.x * 10) && Math.floor(enemy.position.y * 10) === Math.floor(player.position.y * 10)) {
                            player.InGame = false;
                            // Log and send caught packet to player client.
                            console.log("Enemy has eaten player", player.Username, "in lobby with ID:", this.ID);
                            player.conection.send(JSON.stringify({ type: "Caught", data: {} }));
                            this.sholdChekIfendGame = true;
                            break;
                        }
                    }
                    
                    // Chek if player move is valid if it is then update player position to new position based on movement input, this way we can ensure that players can only move to valid positions and that they cannot move through walls or out of bounds, it also makes the game more fair and fun to have a consistent and accurate movement system that players can rely on and that works correctly.
                    if (this.map != null && this.map[Math.floor(player.position.y + player.currentInput.y * PlayerSpeed)] != null && this.map[Math.floor(player.position.y + player.currentInput.y * PlayerSpeed)][Math.floor(player.position.x + player.currentInput.x * PlayerSpeed)] !== 1) {
                        player.position.x += player.currentInput.x * PlayerSpeed;
                        player.position.y += player.currentInput.y * PlayerSpeed;
                    }
                // push to list so we can send it.
                playerInfos.push({
                    Username: player.Username,
                    Position: player.position
                });
            }
        }

        // if we shold chek to stop the game then we do it here
        if (this.sholdChekIfendGame) {
            // we assume we shold not stop the game.
            this.sholdChekIfendGame = false;
            // we check if all the players are in lobby so we assume there is no players left
            let NonePlayersLeft = true;
            // loop trow all players in lobby and if we find one that is still in game then we set NonePlayersLeft to false and break the loop, this way we can efficiently check if there are any players left in the game without having to check every player if we already found one that is still in game, it also makes the code more efficient and faster to check for end game conditions.
            for (const player of this.players) {
                // if the player is ingame then at least one player is in game and ther are players left so set NonePlayersLeft till false
                if (player.InGame === true) {
                    NonePlayersLeft = false;
                    break;
                }
            }

            // if there are no players left we clear enemys intervals and makes the lobby stops the loop.
            if (NonePlayersLeft == true) {
                console.log("Game ended in lobby with ID:", this.ID);
                clearInterval(this.Interval);
                for (const Enemy of this.enemies) {
                    clearInterval(Enemy.Interval);
                    Enemy.Interval = null;
                }
                this.Interval = null;
                this.open = true;
            }
        }
        
        // preparing enemys info for websockets pakets
        let enemyPositions = [];
        for (const enemy of this.enemies) {
            enemyPositions.push({
                x: enemy.position.x,
                y: enemy.position.y
            });
        }    

        // Send updated player info to all players in the lobby
        for (const player of this.players) {
            // if player is ingame and socket is open we send uppdate locations with necesary data
            if (player.InGame === true) {
                if (player.conection.readyState === WebSocket.OPEN) {
                    player.conection.send(JSON.stringify({ type: "UpdateLocations", data: { players: playerInfos, enemyPositions: enemyPositions } }));
                } else {
                    console.log("Player connection Missed", player.Username);
                }
            }
        }
    }
};

// a function for creating a lobby.
function createLobby() {
    // Creates a new lobby with id of serverIDadding.
    const Lobby = new lobby(serverIDadding);
    // sets lobby in lobbty map to key serverIDadding
    lobbys.set(serverIDadding, Lobby);
    // adds 1 to serverIDadding so next lobby gets a different ID.
    serverIDadding++;
    // returns created lobby
    return Lobby;
}

// A* allgorithem for pathfinding, it takes a grid, a start position and an end position and returns the shortest path from start to end as a list of coordinates, this way we can have enemies that can navigate the map and find the player even if there are walls in the way, it also makes the game more fun and challenging to have enemies that can find their way to the player and make it harder for players to win the game.
function FindshortestPath(grid, start, end) {
    // Gets length of the rows and colums
    const rows = grid.length;
    const cols = grid[0].length;

    // Helpfunction to convert coordinates to a string key for maps
    const key = (x, y) => `${x},${y}`;
    
    // Heuristik: manhattan distance guss
    const getH = (x, y) => Math.abs(x - end.x) + Math.abs(y - end.y);

    let openSet = [key(start.x, start.y)];
    let cameFrom = new Map();

    // gscore how long from start to the node
    let gScore = new Map();
    gScore.set(key(start.x, start.y), 0);

    // fscore = gscore + hscore
    let fScore = new Map();
    fScore.set(key(start.x, start.y), getH(start.x, start.y));

    // while we have nodes to explore
    while (openSet.length > 0) {
        // Finde node in openSet with lowest fScore
        let currentKey = openSet.reduce((min, k) => (fScore.get(k) < fScore.get(min) ? k : min), openSet[0]);
        let [cx, cy] = currentKey.split(',').map(Number);

        // If we reached the end, reconstruct the path
        if (cx === end.x && cy === end.y) {
            let path = [];
            while (currentKey) {
                let [px, py] = currentKey.split(',').map(Number);
                path.unshift({ x: px, y: py });
                currentKey = cameFrom.get(currentKey);
            }
            return path;
        }

        // remove current from openSet
        openSet = openSet.filter(k => k !== currentKey);

        // Check neighbors (up, down, left, right)
        const directions = [[0, 1], [0, -1], [1, 0], [-1, 0]];
        for (let [dx, dy] of directions) {
            let nx = cx + dx;
            let ny = cy + dy;

            // check if neighbor is within bounds and not a wall
            if (nx >= 0 && nx < cols && ny >= 0 && ny < rows && grid[ny][nx] !== 1) {
                let neighborKey = key(nx, ny);
                let tentativeGScore = gScore.get(currentKey) + 1;

                // If this path to the neighbor is better than the one we found earlier
                if (tentativeGScore < (gScore.has(neighborKey) ? gScore.get(neighborKey) : Infinity)) {
                    cameFrom.set(neighborKey, currentKey);
                    gScore.set(neighborKey, tentativeGScore);
                    fScore.set(neighborKey, tentativeGScore + getH(nx, ny));

                    if (!openSet.includes(neighborKey)) {
                        openSet.push(neighborKey);
                    }
                }
            }
        }
    }

    return null; // No path found and we should teturn null
}


// function to handle incoming messages from players clients.
function handelemessage(message,socket) {
    // we make the message readebale to are script
    const messageJSON = JSON.parse(message);
    // Get the player object for the player who sent the message.
    const player = players.get(socket);
    
    // If client askes to create a lobby a new lobby is created and the player is added to it
    if (messageJSON.type === "CreateLobby") {
        // if client is allredy in a lobby we do not want to create a nother one so we just send error back and return
        if (player.lobby != null) {
            // Sends error back to players client.
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is already in a lobby" } }));
            // return / stops the function here
            return;
        };
        // creates a new lobby and adds the player to it
        let lobby = createLobby();
        // Adds the player to the lobbys player list
        lobby.players.push(player);
        // bindes players lobby varibale to the lobby
        player.lobby = lobby;
        // Prints that it succesfully created a lobby
        console.log("Lobby created with ID:", lobby.ID);
        // Sends a message back to client that it created and what lobby id it has.
        player.conection.send(JSON.stringify({ type: "LobbyCreated", data: { lobbyID: lobby.ID, success: true } }));
    }; 
    // THis messagetype is for joining lobby and needs a lobby ID.
    if (messageJSON.type === "JoinLobby") {
        // If player is allredy in a lobby this is probobly mistake hack or bug. 
        if (player.lobby != null) {
            // Sends error back to players client.
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is already in a lobby" } }));
            // stops the function here
            return;
        }
        // We try to gett the lobby with the lobby ID the client sent
        const lobby = lobbys.get(messageJSON.data["lobby_id"]);
        // if we cant
        if (lobby == null) {
            // Send error back to client that lobby was not found and return
            socket.send(JSON.stringify({ type: "error", data: {message: "Lobby not found"}}));
            // stop the function here
            return;
        }
        // If we found the lobby but it is curently running a game we do not want new players and that means it is closed
        // If lobby is closed then
        if (!lobby.open) {
            // send error back to the players client that lobby is closed and return
            socket.send(JSON.stringify({ type: "error", data: {message: "Lobby is closed"} }));
            // stop the function here
            return;
        }
        // if we found no problem with player or the lobby we can add them to the lobby.
        // adds the player to the lobbys player list
        lobby.players.push(player);
        // bindes players lobby varibale to the lobby
        player.lobby = lobby;
        // Prints that player has joined the lobby with lobby ID and player username, this is for debugging and to have a log of who joins lobbys and to make sure that the join lobby function is working correctly, it also makes it more fun to see who joins lobbys and to have a record of it on the server.
        console.log("Player", player.Username, "joined lobby with ID:", lobby.ID);
        // Sends a message back to client that it joined and what lobby id it has.
        player.conection.send(JSON.stringify({ type: "LobbyJoined", data: { lobbyID: lobby.ID, success: true } }));
    }
    // if a client sends this it meens to start the game in the lobby thay are in
    if (messageJSON.type === "StartGame") {
        // realese the lobby from the player object from the pointer in the player object
        const lobby = player.lobby;
        // if lobby dose not exist it means that the player is not in a lobby this is becuse thay are hacking or a bug has happend. 
        if (lobby == null) {
            // send a error back to the players client that they are not in a lobby
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is not in a lobby" } }));
            // stop the function here
            return;
        } else {
            // if we are in a lobby (The most likly scenario) we want to close the lobby
            lobby.open = false;
            // prepare the lobby for the game and start the game this includes creating the map and spawning the entitis.
            lobby.PerpareLobby();
            // Start the game send all nececary information and start update loops.
            lobby.startGame();
        }
    };
    // This message type is used when the input frome the user is somthing else then it was before.
    if (messageJSON.type === "UpdateMovementInput") {
        // if this is true someone is messing with my game becuse this is allways betwin -1 and 1.
        if (Math.abs(messageJSON.data["x"]) >= 1 || Math.abs(messageJSON.data["y"]) >= 1) {
            // becuse we do not want cheters in the game we send to the player that we detected the hacking.
            socket.send(JSON.stringify({ type: "error", data: { message: "Hacking detected: Movement input out of bounds" } }));
            // log the hacking in the console
            console.log(player.Username, "sent movement input out of bounds, possible hacking attempt detected, disconnecting player");
            // close the connection
            socket.close();
            // stops the code
            return;
        // if this is true someone sent unnecesssary movment information thas can indecate of hacking and never happends normaly
        } else if ((messageJSON.data["x"] === player.currentInput.x || messageJSON.data["y"] === player.currentInput.y) && player.HasMovedInCurrentGame) {
            // semd error to client that we detected this.
            socket.send(JSON.stringify({ type: "error", data: { message: "Hacking Detected: Movement input unchanged are you hacking?" } }));
            // log detected hacking.
            console.log(player.Username, "sent unchanged movement input, possible hacking attempt detected, disconnecting player");
            // close connection.
            socket.close();
            // stops the function.
            return
        }
        // Set player so thay have a movement input during the game 
        player.HasMovedInCurrentGame = true;
        // update current input for the player.
        player.currentInput.x = messageJSON.data["x"];
        player.currentInput.y = messageJSON.data["y"];
    }
    // This message type is for when a player wants to leave a lobby
    if (messageJSON.type === "LeaveLobby") {
        // get the lobby thay are in
        const lobby = player.lobby;
        // If the player is not in a lobby 
        if (lobby == null) {
            // send error of that we are not in a lobby 
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is not in a lobby" } }));
            // stop function here
            return;
        }
        // deleats player from the lobby player list
        lobby.players = lobby.players.filter((cplayer) => cplayer !== player);
        // Unbind lobby varebale from player
        player.lobby = null;
        // sets players ingame state to false
        player.InGame = false;
        // logs that the player left
        console.log("Player", player.Username, "left lobby with ID:", lobby.ID);
        // if lobby has zero players
        if (lobby.players.length === 0) {
            // log that deliting lobby
            console.log("Lobby is empty, Deleating lobby with ID " + lobby.ID)
            // If a game is running 
            if (lobby.Interval != null) {
                // clear all ennemys intervals
                for (const Enemy of lobby.enemies) {
                    clearInterval(Enemy.Interval);
                    Enemy.Interval = null;
                }
                // clears the lobbys update loop
                clearInterval(lobby.Interval)
                lobby.Interval = null
            }
            // deleate every refrence to lobby so it gets forgoten
            lobbys.delete(lobby.ID)
        }
    }
};

// function for creating the map
function randomizemap() {
    // first we start with a emty map
    const map = [];
    // set a standard goal pso so we can randomize it later
    let goalpos = { x: 0, y: 0 };
    // make the higest randomized goal score 0 the tile with goal score closest to 1 will be the goal.
    let higestgoalscore = 0;
    // make map 100 * 100 tiles
    for (let i = 0; i < 100; i++) {
        const row = [];
        for (let j = 0; j < 100; j++) {
            if (i === 0 || i === 99 || j === 0 || j === 99) {
                row.push(1); // Border walls
                // get a goal score and see if it is the higest if it is chance the goal pos to that tile
                const goalscore = Math.random()
                if (i !== j && goalscore > higestgoalscore) {
                    higestgoalscore = goalscore
                    goalpos = { x: j, y: i }
                }
            } else {
                // if we are not at the corner walls we just randomize the walls
                row.push(Math.random() < 0.4 ? 1 : 0); // 40% chance of being a wall
            }
        };
        // add that row to the map
        map.push(row);
    };
    // place goal on the map
    map[goalpos.y][goalpos.x] = 2;
    // return the map and goal pos
    return [map, goalpos];
};

// create the player class so we can have player objects
class player {
    // defin constroction that needs name of player and socket to bind the player to the object
    constructor(name, socket) {
        // sets all defult valuuse to what thay are
        this.Username = name;
        this.position = { x: 10, y: 10 };
        this.lobby = null;
        this.currentInput = { x: 0, y: 0};
        this.InGame = false;
        this.conection = socket;
        this.HasMovedInCurrentGame = false;
    };
};

// creates the ennemy
class enemy {
    // constructor for the ennemy it needs lobby and position
    constructor(lobby,position) {
        // define position
        this.position = position;
        // define target but not what it is
        this.target = null;
        // the speed of an entity shold be 10% more than a player so thay can chase the player
        this.speed = PlayerSpeed * 3.1;
        // path is now a emty list but A* will calculate that soon for entity
        this.path = [];
        this.pathIndex = 0;
        this.Lobby = lobby;
        // This is used to determin if we need to make a new path
        this.lastBlockToGoTo = { x: 10, y: 10 };
        // if entety cant go somwere it remebers that and never tryes that agen
        this.cantGoTo = [];
        // interval is the entetys game loop
        this.Interval = null;
    };
    // this goas in a strait line to the target position defined
    DumbGoTo(position) {
        // calculates delta x and delta y to see where we need to mover
        const dx = position.x - this.position.x;
        const dy = position.y - this.position.y;
        // if we do not need to move we do not move
        if (dx === 0 && dy === 0) return;
        // if we need to move we move in corect direction
        if (dx > 0) {
            this.position.x += this.speed;
        }
        if (dx < 0) {
            this.position.x -= this.speed;
        }
        if (dy > 0) {
            this.position.y += this.speed;
        }
        if (dy < 0) {
            this.position.y -= this.speed;
        }
    }

    // this is the game loop for the entetys AI system
    GameUpdate() {
        // if we do not have a target or are target is no longer ingame the player died or won we find a new target
        if (this.target == null || this.target.InGame === false) {
            // so we do not know the closet player so it is null
            let closestPlayer = null;
            // we do not know closest distens and cuse nowan exists infinet away so it is infinety
            let closestDistance = Infinity;
            // loop all players in lobby
            for (const player of this.Lobby.players) {
                // if thay are not ingame thay do not need to be cheked
                if (player.InGame === true) {
                    // we chek the dinstens frome player to the entety with the Pythagorean theorem
                    const distance = Math.sqrt((player.position.x - this.position.x) ** 2 + (player.position.y - this.position.y) ** 2);
                    // if the distens was closer then the last closest this is the new closest
                    if (distance < closestDistance) {
                        closestDistance = distance;
                        closestPlayer = player;
                    }
                }
            }
            // taget is the closest player ingame
            this.target = closestPlayer;
        }
        // if we have a target
        if (this.target != null) {
            // we define withc tile entety are positiond as and call it my block
            const myblock = { x: Math.floor(this.position.x), y: Math.floor(this.position.y) };
            // we take the target tile 
            const targetBlock = { x: Math.floor(this.target.position.x), y: Math.floor(this.target.position.y) };
            // If we are on the same tile as the target that means that no wall is in betwean us
            if (myblock.x === targetBlock.x && myblock.y === targetBlock.y) {
                // so justgo in a strait line to the taget
                this.DumbGoTo({ x: this.target.position.x, y: this.target.position.y });
            } else {
                // if that is not the case we must be a smart entety
                const curentTargetBlock = { x: Math.floor(this.target.position.x), y: Math.floor(this.target.position.y) };
                // if we allredy made a path and player stands on the same tile then just go
                if (curentTargetBlock.x === this.lastBlockToGoTo.x && curentTargetBlock.y === this.lastBlockToGoTo.y) {
                    // if path is null or so short that it dose not exist make it
                    if (this.path == null || this.path.length === 0) {
                        // make path index 0 and make the lastBlockGoTo to current also make no target and return
                        this.pathIndex = 0;
                        this.lastBlockToGoTo.x = curentTargetBlock.x;
                        this.lastBlockToGoTo.y = curentTargetBlock.y;
                        this.target = null;
                        return
                    }
                    // if we had a path we shold follow ituntill the end.
                    this.DumbGoTo({ x: this.path[this.pathIndex].x + 0.5, y: this.path[this.pathIndex].y + 0.5 });
                    if (myblock.x === this.path[this.pathIndex].x && myblock.y === this.path[this.pathIndex].y) {
                        this.pathIndex++;
                    }
                } else {
                    // if we need to get path to a diffrent tile caulcalade it here
                    this.path = FindshortestPath(this.Lobby.map, myblock, curentTargetBlock);
                    this.pathIndex = 0;
                    this.lastBlockToGoTo = curentTargetBlock;
                }
            }
        }
    };
}

// when we opens the server suscsesfully for websocket message
wss.on("listening", () => {
    // log Server started
    console.log("Server is sucsessfully started and redy to accept connections");
    // start KeepPlayersConnected loop
    setInterval(() => KeepPlayersConnected(), 1000);
});

// This function is used to make the weboskcet not close. if the websocket dose note transfer any messages in 2 secends it closes
// when the player is not playing a game this functin sends pings with useful information to the clients.
function KeepPlayersConnected() {
    // create a temporary list for all lobbys
    let playerinfolobbys = [];
    // For every player
    players.forEach((player) => {
        // if thay are not in a game (ingame means that thay get packets every 50 ms so no need for a update)
        if (player.InGame === false) {
            // and thay are not in a lobby
            if (player.lobby === null) {
                // and this is the first player that meats this reqerments
                if (playerinfolobbys.length === 0) {
                    // we shold cout eatch lobby into the list with lobby id
                    lobbys.forEach((lobby) => {
                        if (lobby.open) {
                            playerinfolobbys.push({
                                lobbyID: lobby.ID
                            });
                        };
                    });
                }
                // and send it to all players not in a lobby
                player.conection.send(JSON.stringify({type: "AvailebaleLobbys", data:{lobbys: playerinfolobbys}}));
            }
            // if thay are in a lobby
            if (player.lobby != null) {
                // we create a emty player list for that lobby that only going to contain the players namnes
                Players = [];
                // loop all players in that lobby and put thir names in the list
                player.lobby.players.forEach(player => {
                    Players.push({
                        Username: player.Username
                    });
                });
                // send to player client who needed it to ssow to user
                player.conection.send(JSON.stringify({type: "LobbyInfo", data: {lobbyID: player.lobby.ID, Players: Players, gameRunning: !!player.lobby.Interval}}));
            }
        }
    });
}



// This event happens when a new connection has happend
wss.on("connection", (socket) => {
    // when that happens we shoold
    // log it
    console.log("Client connected");
    // make a player object for them with name player and a number and connect player object to socket
    const playerObj = new player("Player " + playerjoinnumber,socket)
    // wait a bit before sending a response to give the client time to react.
    setTimeout(() => {
        // send that it was a success
        playerObj.conection.send(JSON.stringify({ type: "Connection", data: { username: playerObj.Username } }));
        // bind it to the player map
        players.set(socket, playerObj);
    }, 100);
    // add so next player gets one number higer
    playerjoinnumber++;
    // log the username
    console.log("Assigned username:", players.get(socket).Username);

    // if this conection recives any message that shold be sent to the function handelemessage that handels messages
    socket.on("message", (message) => handelemessage(message,socket));

    // connection closes this means that player is leving
    socket.on("close", () => {
        // we shold
        // get the player 
        const player = players.get(socket)
        // log the disconect
        console.log("Client disconnected:", player.Username);
        // chek if thay whare in alobby and delete the frome that
        if (player.lobby != null) {
            const lobby = player.lobby
            lobby.players = lobby.players.filter((cplayer) => cplayer !== player);
            // if the lobby is now emety 
            if (lobby.players.length === 0) {
                // log deletion of that
                console.log("Lobby is empty, Deleating lobby with ID " + lobby.ID)
                // if it had a game started stop that
                if (lobby.Interval != null) {
                    clearInterval(lobby.Interval);
                    for (const Enemy of lobby.enemies) {
                        clearInterval(Enemy.Interval);
                        Enemy.Interval = null;
                    }
                    lobby.Interval = null;
                }
                // delete lobby
                lobbys.delete(lobby.ID)
            }
        }
        // delete player object from socket reference
        players.delete(socket);
    });
});
