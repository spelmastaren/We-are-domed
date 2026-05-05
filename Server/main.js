console.log("Server initialized");
const ws = require("ws");
const wss = new ws.Server({ port: 8080 });
const PlayerSpeed = 0.05;

let playerjoinnumber = 1;
let serverIDadding = 1;

let lobbys = new Map();
let players = new Map();

class lobby {
    constructor(name) {
        // Genererar och avgör om det är möjligt att klara den
        let [map, goal] = randomizemap();
        while (FindshortestPath(map, { x: 10, y: 10 }, { x: goal.x, y: goal.y }) == null) {
            [map, goal] = randomizemap();
        };
        console.log("Lobby created with ID:", name, "and goal at:", goal);
        this.map = map;
        this.ID = name;
        this.players = [];
        this.open = true;
        this.Interval = null;
        this.sholdChekIfendGame = false;
    };

    GameUpdate() {
        // makes a list with all player names and positions
        let playerInfos = [];
        for (const player of this.players) {
            if (player.InGame === true) {
                    if (this.map[Math.floor(player.position.x)][Math.floor(player.position.y)] === 2) {
                        player.InGame = false;
                        console.log("Player", player.Username, "has reached the goal and won the game!");
                        player.conection.send(JSON.stringify({ type: "Winner", data: {} }));
                        this.sholdChekIfendGame = true;
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
                if (player.InGame) {
                    NonePlayersLeft = false;
                    break;
                }
            }
            if (NonePlayersLeft) {
                this.clearInterval(this.Interval);
                this.Interval = null;
                this.open = true;
                let [map, goal] = randomizemap();
                while (FindshortestPath(map, { x: 10, y: 10 }, { x: goal.x, y: goal.y }) == null) {
                    [map, goal] = randomizemap();
                };
                this.map = map;
            }
        }

        // Send updated player info to all players in the lobby
        for (const player of this.players) {
            if (player.conection.readyState === WebSocket.OPEN) {
                player.conection.send(JSON.stringify({ type: "UpdateLocations", data: { players: playerInfos } }));
            } else {
                console.log("Player connection Missed", player.Username);
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

    // Hjälpfunktion för att skapa en unik sträng-nyckel för varje koordinat
    const key = (x, y) => `${x},${y}`;
    
    // Heuristik: Manhattan distance (beräknar kvarvarande steg utan diagonaler)
    const getH = (x, y) => Math.abs(x - end.x) + Math.abs(y - end.y);

    let openSet = [key(start.x, start.y)];
    let cameFrom = new Map();

    // gScore: Kostnaden från start till nuvarande punkt (standard: oändlighet)
    let gScore = new Map();
    gScore.set(key(start.x, start.y), 0);

    // fScore: gScore + hScore (uppskattad total kostnad)
    let fScore = new Map();
    fScore.set(key(start.x, start.y), getH(start.x, start.y));

    while (openSet.length > 0) {
        // Hitta noden i openSet med lägst fScore
        let currentKey = openSet.reduce((min, k) => (fScore.get(k) < fScore.get(min) ? k : min), openSet[0]);
        let [cx, cy] = currentKey.split(',').map(Number);

        // Om vi är framme: Rekonstruera vägen genom att backa via 'cameFrom'
        if (cx === end.x && cy === end.y) {
            let path = [];
            while (currentKey) {
                let [px, py] = currentKey.split(',').map(Number);
                path.unshift({ x: px, y: py });
                currentKey = cameFrom.get(currentKey);
            }
            return path;
        }

        // Ta bort nuvarande från openSet
        openSet = openSet.filter(k => k !== currentKey);

        // Kolla alla 4 grannar (upp, ner, vänster, höger)
        const directions = [[0, 1], [0, -1], [1, 0], [-1, 0]];
        for (let [dx, dy] of directions) {
            let nx = cx + dx;
            let ny = cy + dy;

            // Kontrollera att grannen är inom kartan och inte är en vägg (1)
            if (nx >= 0 && nx < cols && ny >= 0 && ny < rows && grid[ny][nx] !== 1) {
                let neighborKey = key(nx, ny);
                let tentativeGScore = gScore.get(currentKey) + 1;

                // Om denna väg till grannen är bättre än den vi hittat tidigare
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

    return null; // Ingen väg hittades
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
            for (const player of lobby.players) {
                player.InGame = true;
                if (player.conection.readyState === ws.OPEN) {
                    player.conection.send(JSON.stringify({ type: "GameStarted", data: { map: lobby.map } }));
                } else {
                    player.conection.close();
                }
            }
            setInterval(() => lobby.GameUpdate(), 50);
        }
    };
    if (messageJSON.type === "UpdateMovementInput") {
        if (Math.abs(messageJSON.data["x"] * messageJSON.data["y"]) > 0.5) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Movement input out of bounds" } }));
            return;
        }
        player.currentInput.x = messageJSON.data["x"];
        player.currentInput.y = messageJSON.data["y"];
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
                row.push(Math.random() < 0.0 ? 1 : 0); // 0% chance of being a wall
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
    };
};

class enemy {
    constructor() {
        this.position = { x: 0, y: 0 };
    };
};

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
                player.conection.send(JSON.stringify({type: "LobbyInfo", data: {lobbyID: player.lobby.ID, Players: Players, gameRunning: player.lobby.Interval != null}}));
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
