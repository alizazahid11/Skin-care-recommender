import React, { useState, useEffect, useRef } from "react";

function Bot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatBoxRef = useRef(null);

  useEffect(() => {
    // Initial bot message when the chat starts
    setMessages([{ sender: "bot", text: "Hi beauty 😍!" }]);
  }, []);

  const sendMessage = async (payload = null) => {
    const userMessage = payload || input.trim();
    if (!userMessage) return;

    const newMessages = [...messages, { sender: "user", text: userMessage }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          sender: "user123",
        }),
      });

      const data = await response.json();

      // Update messages based on the bot response
      const botMessages = data.map((msg) => ({
        sender: "bot",
        text: msg.text,
        buttons: msg.buttons || [], // Handle buttons
      }));

      setMessages((prev) => [...prev, ...botMessages]);
    } catch (error) {
      console.error("Error communicating with backend:", error.message);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, something went wrong. Please try again later." },
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
    <div style={styles.container}>
      <div ref={chatBoxRef} style={styles.chatBox}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              ...styles.message,
              alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor: msg.sender === "user" ? "#FFB5A7" : "#FEC9C3",
            }}
          >
            {msg.text}

            {/* Render buttons if available */}
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
        {loading && <div style={styles.loading}>Loading...</div>}
      </div>

      <div style={styles.inputContainer}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Write here..."
        />
        <button style={styles.button} onClick={() => sendMessage()}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    height: "100%",
    fontFamily: "Times",
  },
  chatBox: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    padding: "10px",
    overflowY: "auto",
    backgroundColor: "#ffffff",
  },
  message: {
    padding: "10px 15px",
    margin: "5px 0",
    borderRadius: "10px",
    maxWidth: "70%",
    wordWrap: "break-word",
    backgroundColor: "#ff6f91",
    color: "black",
  },
  buttonContainer: {
    marginTop: "5px",
    display: "flex",
    flexWrap: "wrap",
    gap: "5px",
  },
  button: {
    padding: "5px 15px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#FFB5A7",
    color: "black",
    cursor: "pointer",
    boxShadow: "0 0 5px rgba(255, 111, 145, 0.5)",
    transition: "box-shadow 0.3s ease-in-out",
  },
  inputContainer: {
    display: "flex",
    padding: "10px",
    backgroundColor: "#ffffff",
  },
  input: {
    flex: 1,
    padding: "10px",
    borderRadius: "5px",
    marginRight: "10px",
    border: "2px solid rgb(253, 160, 160)",
    backgroundColor: "#fff",
  },
  loading: {
    alignSelf: "center",
    fontStyle: "italic",
    color: "#FFB5A7",
    marginTop: "10px",
  },
};

export default Bot;
