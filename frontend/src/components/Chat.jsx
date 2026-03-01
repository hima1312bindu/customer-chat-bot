import React, { useState } from "react";
import axios from "axios";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // simple session id
  const [sessionId] = useState(() => "session_" + Date.now());

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userText = input;

    // 1️⃣ Add user message immediately
    setMessages(prev => [
      ...prev,
      { sender: "user", text: userText }
    ]);

    setInput("");

    try {
      // 2️⃣ Call backend
      const res = await axios.post(
        "http://localhost:5000/api/chat",
        {
          userId: "test_user",
          sessionId: sessionId,
          message: userText
        }
      );

      console.log("Bot reply:", res.data.reply); // 🔍 debug

      // 3️⃣ Add bot response
      setMessages(prev => [
        ...prev,
        { sender: "bot", text: res.data.reply }
      ]);

    } catch (error) {
      console.error(error);

      // show error in chat
      setMessages(prev => [
        ...prev,
        {
          sender: "bot",
          text: "❌ Server error. Please try again."
        }
      ]);
    }
  };

  return (
    <div
      style={{
        width: "500px",
        margin: "0 auto",
        border: "1px solid #ccc",
        padding: "15px"
      }}
    >
      <div
        style={{
          height: "350px",
          overflowY: "auto",
          marginBottom: "10px",
          padding: "10px",
          background: "#f9f9f9"
        }}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              textAlign: msg.sender === "user" ? "right" : "left",
              margin: "8px 0"
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "8px 12px",
                borderRadius: "12px",
                background:
                  msg.sender === "user" ? "#d4f8c4" : "#e0e0e0"
              }}
            >
              {msg.text}
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: "flex" }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Type your message..."
          style={{ flex: 1, padding: "8px" }}
        />
        <button
          onClick={sendMessage}
          style={{ padding: "8px 15px", marginLeft: "5px" }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;