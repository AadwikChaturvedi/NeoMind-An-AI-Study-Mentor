// timer.js — client-side stopwatch with explicit Start/Pause/Resume/Stop
// controls. On Stop, session data is POSTed to the backend API.

const TIMER_API_URL = "/api/timer/session";

let seconds = 0;
let intervalId = null;
let distractions = 0;

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

function start() {
  seconds = 0;
  distractions = 0;
  distractionCountEl.textContent = "0";
  focusEstimateEl.textContent = "—";
  updateDisplays();
  saveStatus.classList.add("hidden");

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

  const finalDurationMinutes = Math.round((seconds / 60) * 100) / 100;
  const finalFocusScore = estimateFocusScore() ?? 0;

  status.textContent = "Saving session…";
  saveStatus.classList.remove("hidden");
  saveStatus.textContent = "Saving to your study log…";

  try {
    const res = await fetch(TIMER_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        duration: finalDurationMinutes,
        distractions: distractions,
        focus_score: finalFocusScore,
      }),
    });

    if (!res.ok) throw new Error(`Server responded ${res.status}`);

    status.textContent = "Session saved — nice work.";
    saveStatus.textContent = "Saved to your study log.";
  } catch (err) {
    status.textContent = "Session ended — couldn't save it.";
    saveStatus.textContent = "Couldn't reach the server, session wasn't saved.";
    console.error("Failed to save session:", err);
  }

  seconds = 0;
  distractions = 0;
  updateDisplays();
  distractionCountEl.textContent = "0";
  focusEstimateEl.textContent = "—";
}

startBtn.addEventListener("click", start);
pauseBtn.addEventListener("click", pause);
resumeBtn.addEventListener("click", resume);
stopBtn.addEventListener("click", stop);
logDistractionBtn.addEventListener("click", () => {
  distractions++;
  distractionCountEl.textContent = distractions;
});

updateDisplays();
