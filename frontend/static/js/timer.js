// timer.js — client-side stopwatch with mock focus scoring, no backend calls.

let seconds = 0;
let intervalId = null;
let distractions = 0;
let running = false;

const display = document.getElementById("timer-display");
const status = document.getElementById("timer-status");
const startBtn = document.getElementById("start-btn");
const pauseBtn = document.getElementById("pause-btn");
const stopBtn = document.getElementById("stop-btn");
const liveWaveform = document.getElementById("live-waveform");
const livePill = document.getElementById("live-pill");
const distractionCountEl = document.getElementById("distraction-count");
const focusEstimateEl = document.getElementById("focus-estimate");
const logDistractionBtn = document.getElementById("log-distraction");

function format(s) {
  const h = String(Math.floor(s / 3600)).padStart(2, "0");
  const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
  const sec = String(s % 60).padStart(2, "0");
  return `${h}:${m}:${sec}`;
}

function estimateFocusScore() {
  const minutes = seconds / 60;
  if (minutes < 1) return null;
  const penalty = distractions * 6;
  return Math.max(20, Math.min(99, Math.round(95 - penalty + Math.random() * 4)));
}

function tick() {
  seconds++;
  display.textContent = format(seconds);
  const est = estimateFocusScore();
  focusEstimateEl.textContent = est === null ? "—" : est;
}

function start() {
  running = true;
  intervalId = setInterval(tick, 1000);
  status.textContent = "Session in progress";
  startBtn.classList.add("hidden");
  pauseBtn.classList.remove("hidden");
  pauseBtn.textContent = "Pause";
  stopBtn.classList.remove("hidden");
  liveWaveform.classList.remove("hidden");
  livePill.classList.remove("hidden");
  livePill.classList.add("flex");
  logDistractionBtn.disabled = false;
}

function pause() {
  running = false;
  clearInterval(intervalId);
  status.textContent = "Paused";
  liveWaveform.classList.add("hidden");
}

function resume() {
  running = true;
  intervalId = setInterval(tick, 1000);
  status.textContent = "Session in progress";
  liveWaveform.classList.remove("hidden");
}

function stop() {
  running = false;
  clearInterval(intervalId);
  status.textContent = "Session ended — nice work.";
  startBtn.classList.remove("hidden");
  pauseBtn.classList.add("hidden");
  stopBtn.classList.add("hidden");
  liveWaveform.classList.add("hidden");
  livePill.classList.add("hidden");
  livePill.classList.remove("flex");
  logDistractionBtn.disabled = true;

  seconds = 0;
  distractions = 0;
  display.textContent = format(0);
  distractionCountEl.textContent = "0";
  focusEstimateEl.textContent = "—";
}

startBtn.addEventListener("click", start);
pauseBtn.addEventListener("click", () => {
  if (running) { pause(); pauseBtn.textContent = "Resume"; }
  else { resume(); pauseBtn.textContent = "Pause"; }
});
stopBtn.addEventListener("click", stop);
logDistractionBtn.addEventListener("click", () => {
  distractions++;
  distractionCountEl.textContent = distractions;
});
