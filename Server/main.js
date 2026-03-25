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
        this.ID = name;
        this.map = randomizemap();
        this.players = [];
        this.open = true;
        this.Interval = null;
    };

    GameUpdate() {
        // makes a list with all player names and positions
        let playerInfos = [];
        for (const player of this.players) {
                if (this.map != null && this.map[Math.floor(player.position.y + player.currentInput.y * PlayerSpeed)] != null && this.map[Math.floor(player.position.y + player.currentInput.y * PlayerSpeed)][Math.floor(player.position.x + player.currentInput.x * PlayerSpeed)] === 0) {
                    player.position.x += player.currentInput.x * PlayerSpeed;
                    player.position.y += player.currentInput.y * PlayerSpeed;
                }
            playerInfos.push({
                Username: player.Username,
                Position: player.position
            });
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



function handelemessage(message,socket) {
    const messageJSON = JSON.parse(message);
    const player = players.get(socket);
    //console.log("Parsed message:", messageJSON);
    // If client askes to create a lobby a new lobby is created and the player is added to it
    if (messageJSON.type === "CreateLobby") {
        // creates a new lobby and adds the player to it
        let lobby = createLobby();
        lobby.players.push(player);
        player.lobby = lobby;
        console.log("Lobby created with ID:", lobby.ID);
        socket.send(JSON.stringify({ type: "LobbyCreated", data: { lobbyID: lobby.ID, success: true } }));
    };
    // If client askes for all players in a lobby thay gets the username and if its them self or not
    if (messageJSON.type === "ShowPlayersInLobby") {
        const lobby = player.lobby;
        if (lobby == null) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is not in a lobby" } }));
            return;
        } else {
            let PlayerInfos = [];
            lobby.players.forEach(player => {
                PlayerInfos.push({
                    Username: player.Username,
                    ThisIsYou: player === players.get(socket)
                });
            });
            lobby.Interval = setInterval(() => lobby.GameUpdate(), 1);
            socket.send(JSON.stringify({ type: "PlayersInLobby", data: { players:  PlayerInfos} }));
        }
    };    
    if (messageJSON.type === "StartGame") {
        const lobby = player.lobby;
        if (lobby == null) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Player is not in a lobby" } }));
            return;
        } else {
            lobby.open = false;
            for (const player of lobby.players) {
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
        if (messageJSON.data["x"] > 1 || messageJSON.data["x"] < -1 || messageJSON.data["y"] > 1 || messageJSON.data["y"] < -1) {
            socket.send(JSON.stringify({ type: "error", data: { message: "Movement input out of bounds" } }));
            return;
        }
        player.currentInput.x = messageJSON.data["x"];
        player.currentInput.y = messageJSON.data["y"];
    }
};

function randomizemap() {
    const map = [];
    for (let i = 0; i < 100; i++) {
        const row = [];
        for (let j = 0; j < 100; j++) {
            if (i === 0 || i === 99 || j === 0 || j === 99) {
                row.push(1); // Border walls
            } else {
                row.push(Math.random() < 0.4 ? 1 : 0); // 40% chance of being a wall
            }
        };
        map.push(row);
    };
    return map;
};

class player {
    constructor(name, socket) {
        this.Username = name;
        this.position = { x: 10, y: 10 };
        this.lobby = null;
        this.currentInput = { x: 0, y: 0};
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
    players.forEach((player) => {
        if (player.lobby === null || player.lobby.open) {
            player.conection.send(JSON.stringify({type: "PingUpdate", data:{}}));
        }
    });
    console.log("Pinged players")
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
