const mongoose = require("mongoose");

const chatSchema = new mongoose.Schema(
  {
    userId: { type: String },
    sessionId: { type: String, required: true },
    message: { type: String, required: true },
    intent: { type: String },
    emotion: { type: String },
    response: { type: String },
    action: { type: String }
  },
  { timestamps: true }
);

module.exports = mongoose.model("Chat", chatSchema);