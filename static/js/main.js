function appendMessage(role, message) {
  const chatBox = document.getElementById("chat-box");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", role);
  messageDiv.textContent = message;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const question = input.value.trim();
  if (!question) return;

  appendMessage("user", question);
  input.value = "";

  try {
    const response = await fetch("/ask", {
      method: "POST",
      body: new URLSearchParams({ question }),
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    const data = await response.json();
    const aiReply = data.response || "AI did not respond.";
    appendMessage("ai", aiReply);
  } catch (error) {
    appendMessage("ai", "Error: Unable to reach the server.");
  }
}

// Mic button functionality
document.getElementById("mic-btn")?.addEventListener("click", startDictation);

// TTS button
document.getElementById("speak-btn")?.addEventListener("click", speakLastMessage);

function startDictation() {
  if (!("webkitSpeechRecognition" in window)) {
    alert("Speech recognition not supported.");
    return;
  }

  const recognition = new webkitSpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById("user-input").value = transcript;
    sendMessage();
  };

  recognition.onerror = function (event) {
    alert("Speech recognition error: " + event.error);
  };

  recognition.start();
}

function speakLastMessage() {
  const messages = document.querySelectorAll(".message.ai");
  if (messages.length === 0) return;
  const lastMessage = messages[messages.length - 1].textContent;

  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(lastMessage);
  synth.speak(utterance);
}
