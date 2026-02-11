console.log("Server initialized");
const ws = require("ws");
const wss = new ws.Server({ port: 8080 });

let lobbys = new Map();
let players = new Map();

class lobby {
    constructor(name) {
        this.name = name;
        this.map = randomizemap();
        this.players = [];
    };
};

function handelemessage(message) {
    console.log("Received message:", message);
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
    constructor(name) {
        this.Username = name;
        this.position = { x: 0, y: 0 };
        this.lobby = null;

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
    players.set(socket, new player("Player" + players.size));
    socket.on("message", handelemessage);
    socket.on("close", () => {
        console.log("Client disconnected:", players.get(socket).Username);
        players.delete(socket);
    });
});
