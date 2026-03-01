const mongoose = require("mongoose");

const feedbackSchema = new mongoose.Schema(
  {
    sessionId: { type: String, required: true },
    rating: { type: Number, min: 1, max: 5 },
    comment: { type: String }
  },
  { timestamps: true }
);

module.exports = mongoose.model("Feedback", feedbackSchema);