require("dotenv").config();
const cors = require("cors");
const express = require("express");
const cookieParser = require("cookie-parser");
const http = require("http");
const connectDB = require("./config/db");
const authRoutes = require("./routes/authRoutes");
const companyRoutes = require("./routes/companyRoutes");
const pumpRoutes = require("./routes/pumpRoutes");
const userRoutes = require("./routes/userRoutes");
const { setupWebSocket } = require("./websocket/websocket");

const PORT = 5000;
const app = express();

// CORS setup
const corsOptions = {
  origin: "http://localhost:5173",
  credentials: true,
};
app.use(cors(corsOptions));

// Middleware
app.use(express.json());
app.use(cookieParser());

// API routes
app.use("/api/auth", authRoutes);
app.use("/api/company", companyRoutes);
app.use("/api/pumps", pumpRoutes);
app.use("/api/user", userRoutes);

// Database connection
connectDB();

// Basic test route
app.get("/", (req, res) => {
  console.log("Server is working ✅");
  res.send("Server is working ✅");
});

// Add a specific route to test WebSocket endpoint
app.get("/ws", (req, res) => {
  res.status(400).send("WebSocket endpoint - use WebSocket protocol");
});

// Create HTTP server
const server = http.createServer(app);

// Setup WebSocket server and store reference
const wss = setupWebSocket(server);

// Start server
server.listen(PORT, () => {
  console.log(`🚀 HTTP Server running at http://localhost:${PORT}`);
  console.log(`🔌 WebSocket server ready at ws://localhost:${PORT}`);
  console.log("JWT_SECRET configured:", !!process.env.JWT_SECRET);
});

// Improved graceful shutdown
function gracefulShutdown(signal) {
  console.log(`${signal} received, shutting down gracefully...`);

  // Close WebSocket server first
  if (wss) {
    console.log("Closing WebSocket connections...");
    wss.clients.forEach((ws) => {
      ws.close(1000, "Server shutting down");
    });
    wss.close(() => {
      console.log("WebSocket server closed");
    });
  }

  // Close HTTP server
  server.close(() => {
    console.log("HTTP server closed");
    process.exit(0);
  });

  // Force exit after 10 seconds
  setTimeout(() => {
    console.log("Force terminating...");
    process.exit(1);
  }, 10000);
}

process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("SIGINT", () => gracefulShutdown("SIGINT"));
process.on("SIGUSR2", () => gracefulShutdown("SIGUSR2")); // For nodemon
