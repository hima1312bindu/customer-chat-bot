const axios = require("axios");

const AI_BASE_URL = process.env.AI_SERVICE_URL;

exports.predict = async (sessionId, message) => {
  const response = await axios.post(`${AI_BASE_URL}/predict`, {
    session_id: sessionId,
    message: message
  });

  return response.data;
};