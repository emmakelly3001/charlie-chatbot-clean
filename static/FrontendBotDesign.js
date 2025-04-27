document.addEventListener("DOMContentLoaded", () => {
  const windowEl = document.getElementById('chatbot-window');
  const body = document.getElementById('chatbot-body');
  const input = document.getElementById('user-input');

  // Hide chatbot on page load
  windowEl.style.display = "none";

  // Toggle chatbot window
  document.getElementById("chatbot-button").addEventListener("click", () => {
    const wasHidden = windowEl.style.display === "none" || windowEl.style.display === "";
    windowEl.style.display = wasHidden ? "flex" : "none";

    if (wasHidden && body.childElementCount === 0) {
      addMessage("Charlie", "Hi there! I'm Charlie, The NCI FAQ chatbot. Let me know if you have any questions about NCI! 😊");
    }
    
    
    // Add welcome message only if opening the chat for the first time
    if (wasHidden && body.childElementCount === 0) {
      addMessage("Charlie", "Hi there! I'm Charlie, The NCI FAQ chatbot. Let me know if you have any questions about NCI! 😊");
    }
  });

  // Close button functionality
  document.getElementById("chatbot-close").addEventListener("click", () => {
    windowEl.style.display = "none";
  });

  // Send user message and fetch response
  function sendMessage() {
    const msg = input.value.trim();
    if (!msg) return;

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
      const botMsg = document.createElement('div');
      botMsg.className = "chat-bubble bot";
      botMsg.textContent = "Sorry, I couldn't reach the server.";
      body.appendChild(botMsg);
    });

    const userMsg = document.createElement('div');
    userMsg.className = "chat-bubble user";
    userMsg.textContent = msg.charAt(0).toUpperCase() + msg.slice(1);
    body.appendChild(userMsg);
    input.value = "";
  }

  function addMessage(sender, text) {
    const chatBody = document.getElementById("chatbot-body");
    const messageDiv = document.createElement("div");
    messageDiv.className = sender === "Charlie" ? "chat-bubble bot" : "chat-bubble user";
    messageDiv.innerHTML = text;
    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
  }
  

  // Enter key triggers send
  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") sendMessage();
  });

  // Send button triggers send
  document.getElementById("send-button").addEventListener("click", sendMessage);

  // Capitalize first input letter
  input.addEventListener("input", function () {
    if (input.value.length === 1) {
      input.value = input.value.toUpperCase();
    }
  });
});
