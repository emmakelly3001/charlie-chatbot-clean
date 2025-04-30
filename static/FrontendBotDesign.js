//JavaScript for the frontend of the main project

document.addEventListener("DOMContentLoaded", () => {
  // === Get references to DOM elements ===
  const windowEl = document.getElementById('chatbot-window');
  const body = document.getElementById('chatbot-body');
  const input = document.getElementById('user-input');

  // Hide chatbot window on page load
  windowEl.style.display = "none";

  // === Handle opening and closing the chatbot ===

  document.getElementById("chatbot-button").addEventListener("click", () => {
    const wasHidden = windowEl.style.display === "none" || windowEl.style.display === "";

    // Toggle visibility
    windowEl.style.display = wasHidden ? "flex" : "none";

    // Add welcome message only once (when opening for the first time)
    if (wasHidden && body.childElementCount === 0) {
      addMessage("Charlie", "Hi there! I'm Charlie, the NCI FAQ chatbot. Let me know if you have any questions about NCI! 😊");
    }
  });

  document.getElementById("chatbot-close").addEventListener("click", () => {
    windowEl.style.display = "none";
  });

  // === Function to send user message to backend and display response ===

  function sendMessage() {
    const msg = input.value.trim();
    if (!msg) return;  // Ignore empty messages

    // Append user message
    const userMsg = document.createElement('div');
    userMsg.className = "chat-bubble user";
    userMsg.textContent = capitalizeFirstLetter(msg);
    body.appendChild(userMsg);
    input.value = "";

    // Fetch response from backend
    fetch("http://localhost:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    })
    .then(response => response.json())
    .then(data => {
      const botMsg = document.createElement('div');
      botMsg.className = "chat-bubble bot";
      botMsg.innerHTML = data.reply;
      body.appendChild(botMsg);
      body.scrollTop = body.scrollHeight;
    })
    .catch(error => {
      console.error("Error:", error);
      const errorMsg = document.createElement('div');
      errorMsg.className = "chat-bubble bot";
      errorMsg.textContent = "Sorry, I couldn't reach the server.";
      body.appendChild(errorMsg);
    });
  }

  // === Function to add a message (either bot or user) ===

  function addMessage(sender, text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = sender === "Charlie" ? "chat-bubble bot" : "chat-bubble user";
    messageDiv.innerHTML = text;
    body.appendChild(messageDiv);
    body.scrollTop = body.scrollHeight;
  }

  // === Helper function to capitalize first letter ===

  function capitalizeFirstLetter(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  // === Handle sending message on Enter key or Send button ===

  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") sendMessage();
  });

  document.getElementById("send-button").addEventListener("click", sendMessage);

  // Optional: Auto-capitalize first letter as user types
  input.addEventListener("input", function () {
    if (input.value.length === 1) {
      input.value = input.value.toUpperCase();
    }
  });
});
