// dashboard.js — mock data + Chart.js charts, no backend calls yet.

const stats = [
  { label: "Total study hours", value: "126.5h", trend: "+12.4h this month", accent: "violet" },
  { label: "Focus score", value: "82", trend: "+4 pts this week", accent: "cyan" },
  { label: "Study sessions", value: "48", trend: "12 this week", accent: "amber" },
  { label: "Productivity index", value: "8.4", trend: "out of 10", accent: "coral" },
];

const weeklyHours = {
  labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  data: [2.5, 3.2, 1.8, 4.0, 3.5, 5.2, 2.1],
};

const focusTrend = {
  labels: ["S-6", "S-5", "S-4", "S-3", "S-2", "S-1", "Latest"],
  data: [74, 81, 69, 88, 91, 77, 85],
};

function greet() {
  const hour = new Date().getHours();
  const part = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
  const el = document.getElementById("greeting-text");
  if (el) el.textContent = `Good ${part}, Aadwik.`;
}

function renderStats() {
  const el = document.getElementById("stat-cards");
  el.innerHTML = stats.map(s => `
    <div class="rounded-2xl border border-hairline bg-surface p-5">
      <p class="text-xs text-ink2 mb-2">${s.label}</p>
      <p class="font-mono text-2xl">${s.value}</p>
      <p class="text-xs text-${s.accent} mt-2">${s.trend}</p>
    </div>
  `).join("");
}

function renderWeeklyHoursChart() {
  const ctx = document.getElementById("weekly-hours-chart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: weeklyHours.labels,
      datasets: [{
        label: "Hours studied",
        data: weeklyHours.data,
        backgroundColor: "#7C6CFF",
        borderRadius: 6,
        maxBarThickness: 36,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: "#1B2140", borderColor: "#262C4A", borderWidth: 1, padding: 10 },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#8B90AC" } },
        y: { beginAtZero: true, grid: { color: "#1B2140" }, ticks: { color: "#8B90AC" } },
      },
    },
  });
}

function renderFocusTrendChart() {
  const ctx = document.getElementById("focus-trend-chart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "line",
    data: {
      labels: focusTrend.labels,
      datasets: [{
        label: "Focus score",
        data: focusTrend.data,
        borderColor: "#4CC9F0",
        backgroundColor: "rgba(76,201,240,0.15)",
        tension: 0.35,
        fill: true,
        pointBackgroundColor: "#0B0E1A",
        pointBorderColor: "#4CC9F0",
        pointBorderWidth: 2,
        pointRadius: 4,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: "#1B2140", borderColor: "#262C4A", borderWidth: 1, padding: 10 },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#8B90AC" } },
        y: { min: 50, max: 100, grid: { color: "#1B2140" }, ticks: { color: "#8B90AC" } },
      },
    },
  });
}

Chart.defaults.font.family = "Inter, sans-serif";

greet();
renderStats();
renderWeeklyHoursChart();
renderFocusTrendChart();
