console.log("Server initialized");
const ws = require("ws");
const wss = new ws.Server({ port: 8080 });


function handelemessage(message) {
    console.log("Received message:", message);
};



wss.on("connection", (socket) => {
    console.log("Client connected");
    socket.on("message", handelemessage);
    socket.on("close", () => {
        console.log("Client disconnected");
    });
});
