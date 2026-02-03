const { Server } = require("ws");
const jwt = require("jsonwebtoken");
const url = require("url");
const Message = require("../models/Message");
const Conversation = require("../models/Conversation");
const User = require("../models/User");
const { processUserMessage } = require("./assistant");

async function authenticateUser(ws, req) {
  try {
    let token;

    // 1️⃣ Try query parameter first (most reliable)
    const query = url.parse(req.url, true).query;
    if (query.token) {
      token = query.token;
    }

    // 2️⃣ Try cookie
    if (!token && req.headers.cookie) {
      const cookies = Object.fromEntries(
        req.headers.cookie.split(";").map((c) => c.trim().split("="))
      );
      token = cookies.token;
    }

    // 3️⃣ Try WebSocket subprotocol
    if (!token && req.headers["sec-websocket-protocol"]) {
      token = req.headers["sec-websocket-protocol"];
    }

    if (!token) {
      throw new Error("No token provided");
    }

    console.log("Attempting to verify token:", token.substring(0, 10) + "...");

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    ws.userId = decoded.id;

    console.log("User authenticated:", decoded.id);
    return decoded.id;
  } catch (error) {
    console.error("Authentication error:", error.message);
    ws.send(
      JSON.stringify({
        type: "error",
        message: "Authentication failed: " + error.message,
      })
    );
    ws.close(1008, "Authentication failed"); // Policy violation
    throw error;
  }
}

async function findOrCreateConversation(userId, conversationId) {
  try {
    let conversation = null;

    if (conversationId) {
      conversation = await Conversation.findOne({
        _id: conversationId,
        userId,
      });
    }

    if (!conversation) {
      conversation = await Conversation.create({
        title: "Chat with AI Assistant",
        userId,
      });
      console.log("Created new conversation:", conversation._id);
    }

    return conversation;
  } catch (error) {
    console.error("Error finding/creating conversation:", error);
    throw error;
  }
}

async function handleMessage(ws, raw) {
  if (!ws.userId) {
    ws.send(JSON.stringify({ type: "error", message: "Not authenticated" }));
    return;
  }

  let data;
  try {
    data = JSON.parse(raw.toString());
  } catch (err) {
    console.error("Invalid JSON:", err);
    ws.send(JSON.stringify({ type: "error", message: "Invalid JSON format" }));
    return;
  }

  const { type, text, conversationId } = data;
  console.log("Received message type:", type, "from user:", ws.userId);

  if (type === "message") {
    try {
      const conversation = await findOrCreateConversation(
        ws.userId,
        conversationId
      );

      // Save user message first
      const userMsg = await Message.create({
        text,
        senderId: ws.userId,
        conversationId: conversation._id,
      });

      // Send user message back to confirm receipt
      ws.send(JSON.stringify({ type: "message", message: userMsg }));

      // Process message with conversation context
      const reply = await processUserMessage(text, conversation._id); // Pass conversationId!

      if (reply && reply.trim()) {
        const assistantMsg = await Message.create({
          text: reply,
          conversationId: conversation._id,
          senderId: null,
          isSystemMessage: true,
        });

        ws.send(JSON.stringify({ type: "message", message: assistantMsg }));
      } else {
        const defaultReply =
          "I'm still learning how to respond to that. Can you try rephrasing your question?";
        const assistantMsg = await Message.create({
          text: defaultReply,
          conversationId: conversation._id,
          senderId: null,
          isSystemMessage: true,
        });

        ws.send(JSON.stringify({ type: "message", message: assistantMsg }));
      }
    } catch (error) {
      console.error("Error handling message:", error);
      ws.send(
        JSON.stringify({
          type: "error",
          message: "Failed to process message: " + error.message,
        })
      );
    }
  } else if (type === "load_history") {
    try {
      const conversation = await findOrCreateConversation(
        ws.userId,
        conversationId
      );
      const history = await Message.find({ conversationId: conversation._id })
        .sort({ createdAt: 1 })
        .limit(50);

      ws.send(
        JSON.stringify({
          type: "history",
          conversationId: conversation._id,
          title: conversation.title,
          messages: history,
        })
      );
    } catch (error) {
      console.error("Error loading history:", error);
      ws.send(
        JSON.stringify({
          type: "error",
          message: "Failed to load history: " + error.message,
        })
      );
    }
  } else if (type === "new_conversation") {
    try {
      const conversation = await Conversation.create({
        title: "New Conversation",
        userId: ws.userId,
      });

      ws.send(
        JSON.stringify({
          type: "new_conversation",
          conversationId: conversation._id,
          title: conversation.title,
        })
      );
    } catch (error) {
      console.error("Error creating new conversation:", error);
      ws.send(
        JSON.stringify({
          type: "error",
          message: "Failed to create new conversation: " + error.message,
        })
      );
    }
  } else {
    ws.send(
      JSON.stringify({
        type: "error",
        message: "Unknown message type: " + type,
      })
    );
  }
}

function setupWebSocket(server) {
  const wss = new Server({
    server,
    // Remove the path option - let it handle all WebSocket connections
    verifyClient: (info) => {
      // Additional verification can be done here
      console.log("WebSocket connection attempt from:", info.origin);
      return true;
    },
  });

  wss.on("connection", async (ws, req) => {
    console.log("New WebSocket connection attempt...");

    try {
      const userId = await authenticateUser(ws, req);
      console.log("WebSocket connection established for user:", userId);

      // Send welcome message
      ws.send(
        JSON.stringify({
          type: "connected",
          message: "Connected successfully",
        })
      );
    } catch (error) {
      console.error(" WebSocket connection failed:", error.message);
      return; // Connection already closed in authenticateUser
    }

    ws.on("message", (raw) => {
      handleMessage(ws, raw);
    });

    ws.on("close", (code, reason) => {
      console.log(
        `WebSocket connection closed for user ${ws.userId}:`,
        code,
        reason.toString()
      );
    });

    ws.on("error", (error) => {
      console.error("WebSocket error for user", ws.userId, ":", error);
    });
  });

  wss.on("error", (error) => {
    console.error("WebSocket server error:", error);
  });

  console.log(
    " WebSocket server setup complete - listening for all WebSocket connections"
  );
}

module.exports = {
  setupWebSocket,
  authenticateUser,
  handleMessage,
  findOrCreateConversation,
};
