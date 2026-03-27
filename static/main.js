const chatLog = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const statusEl = document.getElementById("status");
const clearBtn = document.getElementById("clear-btn");

function addMessage(text, role, sources = []) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;

  if (sources.length && role === "bot") {
    const src = document.createElement("div");
    src.className = "sources";
    src.textContent = `Sources: ${sources.join(", ")}`;
    bubble.appendChild(src);
  }

  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendMessage(message) {
  statusEl.textContent = "Thinking…";
  input.disabled = true;
  form.querySelector("button").disabled = true;

  addMessage(message, "user");

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Request failed");
    }

    addMessage(data.answer || "(No answer)", "bot", data.sources || []);
    statusEl.textContent = "";
  } catch (err) {
    addMessage(err.message || "Something went wrong.", "bot");
    statusEl.textContent = "";
    statusEl.classList.add("error");
  } finally {
    input.disabled = false;
    form.querySelector("button").disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  sendMessage(message);
  input.value = "";
});

clearBtn.addEventListener("click", () => {
  chatLog.innerHTML = "";
});

// warm-up message
addMessage("Hi! Ask me about the medical documents in your knowledge base.", "bot");
