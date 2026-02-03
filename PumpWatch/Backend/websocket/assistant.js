const { queryFastAPI } = require("../helpers/fastapiHelper");
const Message = require("../models/Message");

async function processUserMessage(userMessage, conversationId) {
  try {
    console.log("Processing user message:", userMessage);
    console.log("Conversation ID:", conversationId);

    // Get recent messages for context
    const recentMessages = await Message.find({ conversationId })
      .sort({ createdAt: -1 })
      .limit(10); // Get last 10 messages

    console.log("Found", recentMessages.length, "recent messages");

    // Build context string from recent conversation
    const context = recentMessages
      .map((m) => (m.senderId ? "User: " : "Assistant: ") + m.text)
      .reverse() // Reverse to get chronological order
      .join("\n");

    console.log("Context being sent:", context.substring(0, 200) + "...");

    // Create full prompt with context + current message
    const fullPrompt = context
      ? `Previous conversation:\n${context}\n\nUser: ${userMessage}\n\nAssistant:`
      : `User: ${userMessage}\n\nAssistant:`;

    // Send the full prompt with context to FastAPI
    const result = await queryFastAPI(fullPrompt);

    if (result && result.answer) {
      console.log("FastAPI response received successfully");
      return result.answer;
    } else {
      console.error("Invalid response from FastAPI:", result);
      return "I'm having trouble understanding your question. Could you please rephrase it?";
    }
  } catch (error) {
    console.error("Error in processUserMessage:", error);
    return "I'm experiencing some technical difficulties. Please try again.";
  }
}

module.exports = { processUserMessage };
