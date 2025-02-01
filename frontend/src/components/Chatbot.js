import React, { useState, useEffect, useRef } from "react";
import { FaRegSmile, FaPaperPlane } from "react-icons/fa";

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatBoxRef = useRef(null);

  const sendMessage = async (messageText = null) => {
    const userMessage = messageText || input.trim();
    if (!userMessage) return;

    // Add user message to chat
    setMessages((prev) => [...prev, { sender: "user", text: userMessage, buttons: [] }]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5009/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sender: "user123", message: userMessage }),
      });

      const data = await response.json();
      console.log("Backend response:", data);

      // Process messages and ensure buttons array always exists
      const botMessages = data.map((msg) => ({
        sender: "bot",
        text: msg.text || "",
        buttons: msg.buttons ? msg.buttons : [], // Ensure buttons is always an array
      }));

      setMessages((prev) => [...prev, ...botMessages]);
    } catch (error) {
      console.error("Error communicating with backend:", error.message);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Oops! Something went wrong. Try again later.", buttons: [] },
      ]);
    } finally {
      setInput("");
      setLoading(false);
    }
  };

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div style={styles.pageContainer}>
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.headerText}>GlowBot</h2>
          <span style={styles.activeStatus}>● active</span>
        </div>

        <p style={styles.disclaimer}>
          This AI-based beauty recommendation is for informational purposes only. <br />
          Please consult a dermatologist or skincare expert for personalized advice.
        </p>

        <div ref={chatBoxRef} style={styles.chatBox}>
          {messages.length === 0 && (
            <div style={styles.botMessage}>
              <span>Hello Beautiful👋 I'm GlowBot, your AI-Powered Skincare Assistant</span>
            </div>
          )}
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                ...styles.message,
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                backgroundColor: msg.sender === "user" ? "#D7BFFD" : "#F0F0F0",
              }}
            >
              {msg.sender === "bot" && <FaRegSmile style={styles.icon} />} {msg.text}

              {/* Render buttons only if they exist */}
              {msg.buttons && msg.buttons.length > 0 && (
                <div style={styles.buttonContainer}>
                  {msg.buttons.map((btn, btnIndex) => (
                    <button
                      key={btnIndex}
                      style={styles.button}
                      onClick={() => sendMessage(btn.payload)}
                    >
                      {btn.title}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div style={styles.loading}>Typing...</div>}
        </div>

        <div style={styles.inputContainer}>
          <input
            style={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about Skincare...."
          />
          <button style={styles.sendButton} onClick={sendMessage}>
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  pageContainer: {
    backgroundColor: "#FEFBF6",
    height: "500px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  container: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    width: "580px",
    height: "580px",
    minHeight: "300px",
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#F5EDED",
    borderRadius: "15px",
    boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
    marginTop: "-95px",
    marginLeft: "-90px",
    overflow: "hidden",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "15px 20px",
    backgroundColor: "BLACK",
    color: "white",
    fontSize: "18px",
    fontWeight: "bold",
    borderTopLeftRadius: "15px",
    borderTopRightRadius: "10px",
  },
  activeStatus: {
    color: "white",
    fontSize: "14px",
    fontWeight: "bold",
  },
  disclaimer: {
    textAlign: "center",
    fontSize: "12px",
    color: "gray",
    padding: "10px 20px",
  },
  chatBox: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    padding: "15px",
    overflowY: "auto",
    minHeight: "300px",
  },
  botMessage: {
    display: "flex",
    alignItems: "center",
    backgroundColor: "#E3E3E3",
    padding: "12px",
    borderRadius: "12px",
    maxWidth: "75%",
    marginBottom: "10px",
  },
  icon: {
    marginRight: "10px",
    color: "#6D6D6D",
  },
  message: {
    padding: "12px 18px",
    margin: "6px 0",
    borderRadius: "12px",
    maxWidth: "70%",
    wordWrap: "break-word",
    color: "black",
  },
  buttonContainer: {
    marginTop: "5px",
    display: "flex",
    flexWrap: "wrap",
    gap: "5px",
  },
  button: {
    padding: "6px 12px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#FFB5A7",
    color: "black",
    cursor: "pointer",
    fontSize: "14px",
  },
  inputContainer: {
    display: "flex",
    alignItems: "center",
    padding: "10px",
    borderTop: "1px solid #ddd",
    marginBottom: "0",
  },
  input: {
    flex: 1,
    padding: "12px",
    borderRadius: "30px",
    border: "1px solid #ccc",
    fontSize: "16px",
    outline: "none",
    paddingLeft: "15px",
  },
  sendButton: {
    padding: "12px",
    marginLeft: "10px",
    border: "none",
    borderRadius: "50%",
    backgroundColor: "black",
    color: "#fff",
    fontSize: "16px",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
};

export default Chatbot;