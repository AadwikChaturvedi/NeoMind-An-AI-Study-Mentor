// mentor.js — mock AI mentor chat, no backend calls.

const seedConversation = [
  { sender: "mentor", text: "Hey Aadwik. I saw your focus score dipped during Linear Algebra yesterday — want to talk through what happened?" },
  { sender: "user", text: "Yeah, I kept checking my phone during the session." },
  { sender: "mentor", text: "That's really common in the first 10 minutes of a session. Try putting your phone in another room next time, and start with the topic you find easiest — it builds momentum before the harder material." },
];

const suggestedPrompts = [
  "Why does my focus drop after 30 minutes?",
  "Help me plan tomorrow's study session",
  "I keep procrastinating on hard topics",
  "How long should my breaks be?",
];

const cannedReplies = [
  { keywords: ["procrastin"], reply: "Try the 2-minute rule: commit to just 2 minutes on the task. Starting is usually the hardest part — momentum takes over after that." },
  { keywords: ["break", "rest"], reply: "For most students, a 5-minute break every 25–30 minutes keeps focus scores highest. Longer sessions need longer breaks — try 15 minutes after 90 minutes of work." },
  { keywords: ["focus", "distract"], reply: "Focus naturally dips in waves. If you notice it dropping, that's a good cue for a short break rather than pushing through." },
  { keywords: ["plan", "schedule"], reply: "Start tomorrow with your hardest subject while your energy is highest, then save lighter review work for later in the day." },
];

const chatWindow = document.getElementById("chat-window");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const promptsEl = document.getElementById("suggested-prompts");

function bubble(sender, text) {
  const wrap = document.createElement("div");
  wrap.className = sender === "user" ? "flex justify-end" : "flex justify-start";
  wrap.innerHTML = `
    <div class="max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
      sender === "user"
        ? "bg-gradient-to-r from-violet to-cyan text-ink"
        : "bg-elevated border border-hairline text-[#EDEEF7]"
    }">${text}</div>
  `;
  chatWindow.appendChild(wrap);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function reply(userText) {
  const lower = userText.toLowerCase();
  const match = cannedReplies.find(r => r.keywords.some(k => lower.includes(k)));
  const text = match ? match.reply : "That's a good question to sit with. Based on your recent sessions, staying consistent with short, focused blocks tends to help more than long unstructured ones.";
  setTimeout(() => bubble("mentor", text), 500);
}

function send(text) {
  const value = (text ?? chatInput.value).trim();
  if (!value) return;
  bubble("user", value);
  chatInput.value = "";
  reply(value);
}

function renderPrompts() {
  promptsEl.innerHTML = suggestedPrompts.map(p => `
    <button class="prompt-chip text-left text-sm rounded-xl border border-hairline px-4 py-3 hover:bg-surface transition">${p}</button>
  `).join("");
  document.querySelectorAll(".prompt-chip").forEach(btn => {
    btn.addEventListener("click", () => send(btn.textContent));
  });
}

seedConversation.forEach(m => bubble(m.sender, m.text));
renderPrompts();

sendBtn.addEventListener("click", () => send());
chatInput.addEventListener("keydown", e => { if (e.key === "Enter") send(); });
