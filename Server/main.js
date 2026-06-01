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
            Enemy.Interval = setInterval(() => Enemy.GameUpdate(), 500);
        }
    }

    GameUpdate() {
        // makes a list with all player names and positions
        let playerInfos = [];
        // loop trow all players in lobby and update their position based on their movement input and check if they have reached the goal or if they have been caught by an enemy, if they have reached the goal send them a winner packet and if they have been caught send them a caught packet, this way we can ensure that players are updated correctly and that the game state is accurate, it also makes sure that players are notified of important events like winning or being caught so they can react accordingly and have a better gaming experience.
        for (const player of this.players) {
            if (player.InGame === true) {
                    if (this.map[Math.floor(player.position.y)][Math.floor(player.position.x)] === 2) {
                        player.InGame = false;
                        console.log("Player", player.Username, "has reached the goal and won the game!");
                        player.conection.send(JSON.stringify({ type: "Winner", data: {} }));
                        this.sholdChekIfendGame = true;
                    }
                    for (const enemy of this.enemies) { 
                        if (Math.floor(enemy.position.x * 10) === Math.floor(player.position.x * 10) && Math.floor(enemy.position.y * 10) === Math.floor(player.position.y * 10)) {
                            player.InGame = false;
                            console.log("Enemy has eaten player", player.Username, "in lobby with ID:", this.ID);
                            player.conection.send(JSON.stringify({ type: "Caught", data: {} }));
                            this.sholdChekIfendGame = true;
                            break;
                        }
                    }

                    if (this.map != null && this.map[Math.floor(player.position.y + player.currentInput.y * PlayerSpeed)] != null && this.map[Math.floor(player.position.y + player.currentInput.y * PlayerSpeed)][Math.floor(player.position.x + player.currentInput.x * PlayerSpeed)] !== 1) {
                        player.position.x += player.currentInput.x * PlayerSpeed;
                        player.position.y += player.currentInput.y * PlayerSpeed;
                    }
                playerInfos.push({
                    Username: player.Username,
                    Position: player.position
                });
            }
        }

        if (this.sholdChekIfendGame) {
            this.sholdChekIfendGame = false;
            let NonePlayersLeft = true;
            for (const player of this.players) {
                if (player.InGame === true) {
                    NonePlayersLeft = false;
                    break;
                }
            }
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
        let enemyPositions = [];
        for (const enemy of this.enemies) {
            enemyPositions.push({
                x: enemy.position.x,
                y: enemy.position.y
            });
        }    
        // Send updated player info to all players in the lobby
        for (const player of this.players) {
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

function createLobby() {
    const Lobby = new lobby(serverIDadding);
    lobbys.set(serverIDadding, Lobby);
    serverIDadding++;
    return Lobby;
}

function FindshortestPath(grid, start, end) {
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

    return null; // No path found
}

function handelemessage(message,socket) {
    const messageJSON = JSON.parse(message);
    const player = players.get(socket);
    //console.log("Parsed message:", messageJSON);
    // If client askes to create a lobby a new lobby is created and the player is added to it
    if (messageJSON.type === "CreateLobby") {
        if (player.lobby != null) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is already in a lobby" } }));
            return;
        };
        // creates a new lobby and adds the player to it
        let lobby = createLobby();
        lobby.players.push(player);
        player.lobby = lobby;
        console.log("Lobby created with ID:", lobby.ID);
        player.conection.send(JSON.stringify({ type: "LobbyCreated", data: { lobbyID: lobby.ID, success: true } }));
    }; 
    if (messageJSON.type === "JoinLobby") {
        if (player.lobby != null) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is already in a lobby" } }));
            return;
        }
        const lobby = lobbys.get(messageJSON.data["lobby_id"]);
        if (lobby == null) {
            socket.send(JSON.stringify({ type: "error", data: {message: "Lobby not found"}}));
            return;
        }
        if (!lobby.open) {
            socket.send(JSON.stringify({ type: "error", data: {message: "Lobby is closed"} }));
            return;
        }
        lobby.players.push(player);
        player.lobby = lobby;
        console.log("Player", player.Username, "joined lobby with ID:", lobby.ID);
        player.conection.send(JSON.stringify({ type: "LobbyJoined", data: { lobbyID: lobby.ID, success: true } }));
    }
    if (messageJSON.type === "StartGame") {
        const lobby = player.lobby;
        if (lobby == null) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is not in a lobby" } }));
            return;
        } else {
            lobby.open = false;
            lobby.PerpareLobby();
            lobby.startGame();
        }
    };
    if (messageJSON.type === "UpdateMovementInput") {
        if (Math.abs(messageJSON.data["x"]) >= 1 || Math.abs(messageJSON.data["y"]) >= 1) {
            socket.send(JSON.stringify({ type: "error", data: { message: "HAcking detected: Movement input out of bounds" } }));
            console.log(player.Username, "sent movement input out of bounds, possible hacking attempt detected, disconnecting player");
            socket.close();
            return;
        } else if ((messageJSON.data["x"] === player.currentInput.x || messageJSON.data["y"] === player.currentInput.y) && player.HasMovedInCurrentGame) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Hacking Detected: Movement input unchanged are you hacking?" } }));
            console.log(player.Username, "sent unchanged movement input, possible hacking attempt detected, disconnecting player");
            socket.close();
            return
        }
        player.HasMovedInCurrentGame = true;
        player.currentInput.x = messageJSON.data["x"];
        player.currentInput.y = messageJSON.data["y"];
    }
    if (messageJSON.type === "LeaveLobby") {
        const lobby = player.lobby;
        if (lobby == null) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is not in a lobby" } }));
            return;
        }
        lobby.players = lobby.players.filter((cplayer) => cplayer !== player);
        player.lobby = null;
        player.InGame = false;
        console.log("Player", player.Username, "left lobby with ID:", lobby.ID);
        if (lobby.players.length === 0) {
            console.log("Lobby is empty, Deleating lobby with ID " + lobby.ID)
            if (lobby.Interval != null) {
                clearInterval(lobby.Interval)
                lobby.Interval = null
            }
            lobbys.delete(lobby.ID)
        }
    }
};

function randomizemap() {
    const map = [];
    
    let goalpos = { x: 0, y: 0 };
    for (let i = 0; i < 100; i++) {
        const row = [];
        higestgoalscore = 0;
        for (let j = 0; j < 100; j++) {
            if (i === 0 || i === 99 || j === 0 || j === 99) {
                row.push(1); // Border walls
                const goalscore = Math.random()
                if (i !== j && goalscore > higestgoalscore) {
                    higestgoalscore = goalscore
                    goalpos = { x: j, y: i }
                }
            } else {
                row.push(Math.random() < 0.4 ? 1 : 0); // 40% chance of being a wall
            }
        };
        map.push(row);
    };
    map[goalpos.y][goalpos.x] = 2; // Place the goal    
    return [map, goalpos];
};

class player {
    constructor(name, socket) {
        this.Username = name;
        this.position = { x: 10, y: 10 };
        this.lobby = null;
        this.currentInput = { x: 0, y: 0};
        this.InGame = false;
        this.conection = socket;
        this.HasMovedInCurrentGame = false;
    };
};

class enemy {
    constructor(lobby,position) {
        this.position = position;
        this.target = null;
        this.speed = PlayerSpeed * 1.1;
        this.path = [];
        this.pathIndex = 0;
        this.Lobby = lobby;
        this.lastBlockToGoTo = { x: 10, y: 10 };
        this.cantGoTo = [];
        this.Interval = null;
    };
    DumbGoTo(position) {
        const dx = position.x - this.position.x;
        const dy = position.y - this.position.y;
        if (dx === 0 && dy === 0) return;
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

    GameUpdate() {
        if (this.target == null || this.target.InGame === false) {
            let closestPlayer = null;
            let closestDistance = Infinity;
            for (const player of this.Lobby.players) {
                if (player.InGame === true) {
                    const distance = Math.sqrt((player.position.x - this.position.x) ** 2 + (player.position.y - this.position.y) ** 2);
                    if (distance < closestDistance) {
                        closestDistance = distance;
                        closestPlayer = player;
                    }
                }
            }
            this.target = closestPlayer;
        }
        if (this.target != null) {
            const myblock = { x: Math.floor(this.position.x), y: Math.floor(this.position.y) };
            const targetBlock = { x: Math.floor(this.target.position.x), y: Math.floor(this.target.position.y) };
            if (myblock.x === targetBlock.x && myblock.y === targetBlock.y) {
                this.DumbGoTo({ x: this.target.position.x, y: this.target.position.y });
            } else {
                const curentTargetBlock = { x: Math.floor(this.target.position.x), y: Math.floor(this.target.position.y) };
                if (curentTargetBlock.x === this.lastBlockToGoTo.x && curentTargetBlock.y === this.lastBlockToGoTo.y) {
                    if (this.path == null || this.path.length === 0) {
                        if (this.cantGoTo.includes({ x: curentTargetBlock.x, y: curentTargetBlock.y })) {
                            this.path = FindshortestPath(this.Lobby.map, myblock, curentTargetBlock);
                        }
                        if (this.path == null && !this.cantGoTo.includes({ x: curentTargetBlock.x, y: curentTargetBlock.y })) {
                            this.cantGoTo.push({ x: curentTargetBlock.x, y: curentTargetBlock.y });
                        }
                        this.pathIndex = 0;
                        this.lastBlockToGoTo.x = curentTargetBlock.x;
                        this.lastBlockToGoTo.y = curentTargetBlock.y;
                    }
                    if (this.path == null || this.path.length === 0) {
                        this.target = null;
                        return
                    };
                    this.DumbGoTo({ x: this.path[this.pathIndex].x + 0.5, y: this.path[this.pathIndex].y + 0.5 });
                    if (myblock.x === this.path[this.pathIndex].x && myblock.y === this.path[this.pathIndex].y) {
                        this.pathIndex++;
                    }
                } else {
                    this.path = FindshortestPath(this.Lobby.map, myblock, curentTargetBlock);
                    this.pathIndex = 0;
                    this.lastBlockToGoTo = curentTargetBlock;
                }
            }
        }
    };
}

wss.on("listening", () => {
    console.log("Server is sucsessfully started and redy to accept connections");
    setInterval(() => KeepPlayersConnected(), 1000);
});

function KeepPlayersConnected() {
    let playerinfolobbys = [];
    players.forEach((player) => {
        if (player.InGame === false) {
            if (player.lobby === null) {
                if (playerinfolobbys.length === 0) {
                    lobbys.forEach((lobby) => {
                        if (lobby.open) {
                            playerinfolobbys.push({
                                lobbyID: lobby.ID
                            });
                        };
                    });
                }
                player.conection.send(JSON.stringify({type: "AvailebaleLobbys", data:{lobbys: playerinfolobbys}}));
            }
            if (player.lobby != null) {
                Players = [];
                player.lobby.players.forEach(player => {
                    Players.push({
                        Username: player.Username
                    });
                });
                player.conection.send(JSON.stringify({type: "LobbyInfo", data: {lobbyID: player.lobby.ID, Players: Players, gameRunning: !!player.lobby.Interval}}));
            }
        }
    });
}




wss.on("connection", (socket) => {
    console.log("Client connected");
    players.set(socket, new player("Player " + playerjoinnumber,socket));
    socket.send(JSON.stringify({ type: "Connection", data: { username: players.get(socket).Username } }));
    playerjoinnumber++;
    console.log("Assigned username:", players.get(socket).Username);

    socket.on("message", (message) => handelemessage(message,socket));

    socket.on("close", () => {
        const player = players.get(socket)
        console.log("Client disconnected:", player.Username);
        if (player.lobby != null) {
            const lobby = player.lobby
            lobby.players = lobby.players.filter((cplayer) => cplayer !== player);
            if (lobby.players.length === 0) {
                console.log("Lobby is empty, Deleating lobby with ID " + lobby.ID)
                if (lobby.Interval != null) {
                    clearInterval(lobby.Interval)
                    lobby.Interval = null
                }
                lobbys.delete(lobby.ID)
            }
        }
        players.delete(socket);
    });
});
