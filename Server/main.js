console.log("Server initialized");
const ws = require("ws");
const wss = new ws.Server({ port: 8080 });

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
    };
};

function createLobby() {
    const lobby = new lobby(serverIDadding);
    lobbys.set(serverIDadding, lobby);
    serverIDadding++;
    return lobby;
}



function handelemessage(message,socket) {
    console.log("Received message:", message);
    const messageJSON = JSON.parse(message);
    const player = players.get(socket);
    console.log("Parsed message:", messageJSON);
    // If client askes to create a lobby a new lobby is created and the player is added to it
    if (messageJSON.type === "CreateLobby") {
        // creates a new lobby and adds the player to it
        const lobby = createLobby();
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

            socket.send(JSON.stringify({ type: "PlayersInLobby", data: { players:  PlayerInfos} }));
        }
    };    
};

function randomizemap() {
    const map = [];
    for (let i = 0; i < 10; i++) {
        const row = [];
        for (let j = 0; j < 10; j++) {
            row.push(Math.random() < 0.4 ? 1 : 0); // 20% chance of being a wall
        };
        map.push(row);
    };
    return map;
};

class player {
    constructor(name, socket) {
        this.Username = name;
        this.position = { x: 0, y: 0 };
        this.lobby = null;
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
});


wss.on("connection", (socket) => {
    console.log("Client connected");
    players.set(socket, new player("Player " + playerjoinnumber,socket));
    socket.send(JSON.stringify({ type: "Connection", data: { username: players.get(socket).Username } }));
    playerjoinnumber++;


    console.log("Assigned username:", players.get(socket).Username);
    socket.on("message", (message) => handelemessage(message,socket));
    socket.on("close", () => {
        console.log("Client disconnected:", players.get(socket).Username);
        players.delete(socket);
    });
});
