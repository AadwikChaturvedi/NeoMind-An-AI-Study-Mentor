// timer.js — Study Timer logic + backend connection.
//
// On Stop, session data is POSTed to POST /sessions (the general
// sessions API — see backend/app/routes/sessions.py). That endpoint
// expects integers, so duration is rounded to whole minutes before
// sending.

const SESSIONS_API_URL = "/sessions";

let seconds = 0;
let intervalId = null;
let distractions = 0;
let lastFailedPayload = null; // kept around so "Retry save" can resend it

const display = document.getElementById("timer-display");
const sessionDurationEl = document.getElementById("session-duration");
const status = document.getElementById("timer-status");
const startBtn = document.getElementById("start-btn");
const pauseBtn = document.getElementById("pause-btn");
const resumeBtn = document.getElementById("resume-btn");
const stopBtn = document.getElementById("stop-btn");
const liveWaveform = document.getElementById("live-waveform");
const livePill = document.getElementById("live-pill");
const distractionCountEl = document.getElementById("distraction-count");
const focusEstimateEl = document.getElementById("focus-estimate");
const logDistractionBtn = document.getElementById("log-distraction");
const saveStatus = document.getElementById("save-status");
const retrySaveBtn = document.getElementById("retry-save-btn");

function formatClock(s) {
  const h = String(Math.floor(s / 3600)).padStart(2, "0");
  const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
  const sec = String(s % 60).padStart(2, "0");
  return `${h}:${m}:${sec}`;
}

function updateDisplays() {
  display.textContent = formatClock(seconds);
  sessionDurationEl.textContent = `${Math.floor(seconds / 60)} min`;
}

function estimateFocusScore() {
  const minutes = seconds / 60;
  if (minutes < 1) return null;
  const penalty = distractions * 6;
  return Math.max(20, Math.min(99, Math.round(95 - penalty + Math.random() * 4)));
}

function tick() {
  seconds++;
  updateDisplays();
  const est = estimateFocusScore();
  focusEstimateEl.textContent = est === null ? "—" : est;
}

function showButtons({ start = false, pause = false, resume = false, stop = false }) {
  startBtn.classList.toggle("hidden", !start);
  pauseBtn.classList.toggle("hidden", !pause);
  resumeBtn.classList.toggle("hidden", !resume);
  stopBtn.classList.toggle("hidden", !stop);
}

// Sends session data to the backend. Returns { ok, message } instead of
// throwing, so callers (stop() and the retry button) can just show
// whatever message comes back without duplicating try/catch logic.
async function saveSession(payload) {
  try {
    const res = await fetch(SESSIONS_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      return { ok: true, message: "Saved to your study log." };
    }

    // Server responded, but rejected the request (bad data, server error, etc.)
    if (res.status >= 400 && res.status < 500) {
      return { ok: false, message: "The server rejected this session's data. It wasn't saved." };
    }
    return { ok: false, message: "The server had a problem saving this session. Try again shortly." };
  } catch (err) {
    // fetch() itself threw — almost always a network/connectivity issue
    console.error("Failed to reach the server:", err);
    return { ok: false, message: "Couldn't reach the server. Check your connection and try again." };
  }
}

function start() {
  seconds = 0;
  distractions = 0;
  lastFailedPayload = null;
  distractionCountEl.textContent = "0";
  focusEstimateEl.textContent = "—";
  updateDisplays();
  saveStatus.classList.add("hidden");
  retrySaveBtn.classList.add("hidden");

  intervalId = setInterval(tick, 1000);
  status.textContent = "Session in progress";
  showButtons({ pause: true, stop: true });
  liveWaveform.classList.remove("hidden");
  livePill?.classList.remove("hidden");
  livePill?.classList.add("flex");
  logDistractionBtn.disabled = false;
}

function pause() {
  clearInterval(intervalId);
  status.textContent = "Paused";
  showButtons({ resume: true, stop: true });
  liveWaveform.classList.add("hidden");
}

function resume() {
  intervalId = setInterval(tick, 1000);
  status.textContent = "Session in progress";
  showButtons({ pause: true, stop: true });
  liveWaveform.classList.remove("hidden");
}

async function stop() {
  clearInterval(intervalId);
  showButtons({ start: true });
  liveWaveform.classList.add("hidden");
  livePill?.classList.add("hidden");
  livePill?.classList.remove("flex");
  logDistractionBtn.disabled = true;

  const payload = {
    duration: Math.round(seconds / 60), // whole minutes — /sessions expects an int
    distractions: distractions,
    focus_score: estimateFocusScore() ?? 0,
  };

  status.textContent = "Saving session…";
  saveStatus.classList.remove("hidden");
  saveStatus.textContent = "Saving to your study log…";
  retrySaveBtn.classList.add("hidden");

  const result = await saveSession(payload);
  saveStatus.textContent = result.message;

  if (result.ok) {
    status.textContent = "Session saved — nice work.";
    lastFailedPayload = null;
  } else {
    status.textContent = "Session ended";
    lastFailedPayload = payload;
    retrySaveBtn.classList.remove("hidden");
  }

  seconds = 0;
  distractions = 0;
  updateDisplays();
  distractionCountEl.textContent = "0";
  focusEstimateEl.textContent = "—";
}

async function retrySave() {
  if (!lastFailedPayload) return;
  retrySaveBtn.classList.add("hidden");
  saveStatus.textContent = "Retrying…";

  const result = await saveSession(lastFailedPayload);
  saveStatus.textContent = result.message;

  if (result.ok) {
    lastFailedPayload = null;
  } else {
    retrySaveBtn.classList.remove("hidden");
  }
}

startBtn.addEventListener("click", start);
pauseBtn.addEventListener("click", pause);
resumeBtn.addEventListener("click", resume);
stopBtn.addEventListener("click", stop);
retrySaveBtn.addEventListener("click", retrySave);
logDistractionBtn.addEventListener("click", () => {
  distractions++;
  distractionCountEl.textContent = distractions;
});

updateDisplays();
