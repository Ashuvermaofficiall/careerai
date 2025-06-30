const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const uploadInput = document.getElementById("resume-upload");
const jobBtn = document.getElementById("job-btn");
const scoreBtn = document.getElementById("score-btn");

function appendMessage(sender, message) {
    const div = document.createElement("div");
    div.classList.add("message", sender);
    div.innerText = message;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const msg = userInput.value.trim();
    if (!msg) return;
    appendMessage("user", msg);
    userInput.value = "";
    const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: msg })
    });
    const data = await res.json();
    appendMessage("bot", data.response);
    speak(data.response);
}

sendBtn.onclick = sendMessage;
userInput.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
});

micBtn.onclick = () => {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Mic not supported");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.start();
    recognition.onresult = e => {
        userInput.value = e.results[0][0].transcript;
        sendMessage();
    };
};

function speak(message) {
    fetch("/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    }).then(res => res.json())
      .then(data => {
        const audio = new Audio(data.url);
        audio.play();
    });
}

uploadInput.onchange = () => {
    const file = uploadInput.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("resume", file);
    appendMessage("user", `📄 Uploaded: ${file.name}`);
    fetch("/upload", {
        method: "POST",
        body: fd
    }).then(res => res.json())
      .then(data => {
        appendMessage("bot", data.response);
        speak(data.response);
    });
};

jobBtn.onclick = () => {
    const role = prompt("Enter job title (e.g. Python Developer):") || "developer";
    fetch("/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role })
    }).then(res => res.json())
      .then(data => {
        appendMessage("bot", "🔎 Jobs:\n" + data.response);
        speak("Here are some jobs I found.");
    });
};

scoreBtn.onclick = () => {
    const lastResume = document.querySelector(".message.user:last-child");
    if (!lastResume) return alert("Upload resume first!");
    fetch("/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: lastResume.innerText })
    }).then(res => res.json())
      .then(data => {
        appendMessage("bot", data.response);
        speak(data.response);
    });
};