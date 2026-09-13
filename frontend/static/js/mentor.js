// mentor.js — AI Mentor chat UI, connected to POST /mentor/chat.
//
// Sends the user's message to the backend, which calls Gemini
// server-side (see backend/app/services/gemini_service.py) and
// returns { reply: "..." }. A typing indicator shows while waiting,
// and any failure is rendered as a message instead of failing silently.

const MENTOR_API_URL = "/mentor/chat";

const chatHistory = [
  { sender: "mentor", text: "Hey Aadwik. I saw your focus score dipped during Linear Algebra yesterday — want to talk through what happened?" },
];

const suggestedPrompts = [
  "Why does my focus drop after 30 minutes?",
  "Help me plan tomorrow's study session",
  "I keep procrastinating on hard topics",
  "How long should my breaks be?",
];

const chatWindow = document.getElementById("chat-window");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const promptsEl = document.getElementById("suggested-prompts");

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function renderMessage({ sender, text }) {
  const wrap = document.createElement("div");
  wrap.className = sender === "user" ? "flex justify-end" : "flex justify-start";

  const bubble = document.createElement("div");
  bubble.className =
    sender === "user"
      ? "max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed bg-gradient-to-r from-violet to-cyan text-ink"
      : "max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed bg-elevated border border-hairline text-[#EDEEF7] markdown-body";

  if (sender === "mentor") {
    // Gemini's replies come back as Markdown (and sometimes LaTeX math),
    // e.g. "**bold**", "### heading", "$$x^2$$" — parse it into real HTML
    // instead of showing the raw characters. DOMPurify strips anything
    // dangerous before it touches the page.
    const html = marked.parse(text);
    bubble.innerHTML = DOMPurify.sanitize(html);

    if (window.renderMathInElement) {
      renderMathInElement(bubble, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\[", right: "\\]", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false },
        ],
        throwOnError: false,
      });
    }
  } else {
    // User input is never parsed as Markdown/HTML — always plain text.
    bubble.textContent = text;
  }

  wrap.appendChild(bubble);
  chatWindow.appendChild(wrap);
  scrollToBottom();
}

function addMessage(sender, text) {
  chatHistory.push({ sender, text });
  renderMessage({ sender, text });
}

// --- Loading animation while waiting for Gemini ---
function showTypingIndicator() {
  const wrap = document.createElement("div");
  wrap.id = "typing-indicator";
  wrap.className = "flex justify-start";
  wrap.innerHTML = `
    <div class="bg-elevated border border-hairline rounded-2xl px-4 py-3 flex gap-1 items-center">
      <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
    </div>
  `;
  chatWindow.appendChild(wrap);
  scrollToBottom();
}

function removeTypingIndicator() {
  document.getElementById("typing-indicator")?.remove();
}

// --- Send the message, get Gemini's response back ---
async function replyTo(userText) {
  showTypingIndicator();

  try {
    const res = await fetch(MENTOR_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText }),
    });

    removeTypingIndicator();

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}));
      addMessage("mentor", errorBody.detail || "The mentor couldn't respond right now. Try again in a moment.");
      return;
    }

    const data = await res.json();
    addMessage("mentor", data.reply);
  } catch (err) {
    removeTypingIndicator();
    console.error("Failed to reach the mentor:", err);
    addMessage("mentor", "Couldn't reach the mentor right now. Check your connection and try again.");
  }
}

function send(text) {
  const value = (text ?? chatInput.value).trim();
  if (!value) return;
  addMessage("user", value);
  chatInput.value = "";
  replyTo(value);
}

function renderPrompts() {
  promptsEl.innerHTML = suggestedPrompts.map(p => `
    <button class="prompt-chip text-left text-sm rounded-xl border border-hairline px-4 py-3 hover:bg-surface transition">${p}</button>
  `).join("");
  document.querySelectorAll(".prompt-chip").forEach(btn => {
    btn.addEventListener("click", () => send(btn.textContent));
  });
}

function init() {
  chatHistory.forEach(renderMessage);
  renderPrompts();
}

sendBtn.addEventListener("click", () => send());
chatInput.addEventListener("keydown", e => { if (e.key === "Enter") send(); });

init();
