import React from "react";
import Chat from "./components/Chat.jsx";

function App() {
  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1 style={{ textAlign: "center" }}>Customer Support Chatbot</h1>
      <Chat />
    </div>
  );
}

export default App;