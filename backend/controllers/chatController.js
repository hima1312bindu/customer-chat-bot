const Chat = require("../models/Chat");
const Feedback = require("../models/Feedback");
const { predict } = require("../services/aiService");

exports.handleChat = async (req, res) => {
  try {
    const { userId, sessionId, message } = req.body;

    // Call AI Service
    const ai = await predict(sessionId, message);

    // Save chat
    await Chat.create({
      userId,
      sessionId,
      message,
      intent: ai.intent,
      emotion: ai.emotion,
      response: ai.bot_reply,
      action: ai.action
    });

    // Escalation handling
    if (ai.action === "escalate_to_human") {
      // Here you can:
      // - create support ticket
      // - notify admin dashboard
      // - send email/slack
      console.log("🚨 Escalation requested for session:", sessionId);
    }

    res.json({
      reply: ai.bot_reply,
      intent: ai.intent,
      emotion: ai.emotion,
      action: ai.action
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.submitFeedback = async (req, res) => {
  try {
    const { sessionId, rating, comment } = req.body;

    const feedback = await Feedback.create({
      sessionId,
      rating,
      comment
    });

    res.json({
      message: "✅ Feedback submitted successfully",
      feedback
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};