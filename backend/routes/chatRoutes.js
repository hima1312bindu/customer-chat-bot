const express = require("express");
const router = express.Router();
const {
  handleChat,
  submitFeedback
} = require("../controllers/chatController");

router.post("/chat", handleChat);
router.post("/feedback", submitFeedback);

module.exports = router;