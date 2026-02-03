const axios = require("axios");

async function queryFastAPI(question) {
  try {
    console.log("Sending question to FastAPI:", question);

    // Ensure question is valid
    if (!question || typeof question !== "string") {
      throw new Error("Invalid question parameter");
    }

    // Method: Direct string formatting (most reliable for FastAPI)
    const formData = `question=${encodeURIComponent(question.trim())}`;
    console.log("Form data being sent:", formData);

    const response = await axios({
      method: "POST",
      url: "http://localhost:8000/query",
      data: formData,
      timeout: 30000,
    });

    console.log("FastAPI response received:", response.data);
    return response.data;
  } catch (error) {
    console.error(
      "Error calling FastAPI:",
      error.response?.data || error.message
    );

    // Return a fallback response that matches expected structure
    return {
      question: question,
      answer:
        "I'm having trouble processing your request right now. Please try again later.",
      sources: { texts: [], images: [] },
    };
  }
}

module.exports = { queryFastAPI };
