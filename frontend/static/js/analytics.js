// analytics.js — fetches real aggregated data from GET /analytics/summary
// and renders it with Chart.js. No mock data.

const ANALYTICS_API_URL = "/analytics/summary";

Chart.defaults.font.family = "Inter, sans-serif";
Chart.defaults.color = "#8B90AC";

const chartOptionsBase = {
  responsive: true,
  plugins: {
    legend: { display: false },
    tooltip: { backgroundColor: "#1B2140", borderColor: "#262C4A", borderWidth: 1, padding: 10 },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: "#8B90AC" } },
    y: { beginAtZero: true, grid: { color: "#1B2140" }, ticks: { color: "#8B90AC" } },
  },
};

function renderStatCards(stats) {
  const cards = [
    { label: "Sessions logged", value: stats.sessions_logged, accent: "violet" },
    { label: "Total distractions", value: stats.total_distractions, accent: "coral" },
    { label: "Avg. distractions / session", value: stats.average_per_session, accent: "amber" },
    { label: "Distraction-free sessions", value: stats.distraction_free_sessions, accent: "cyan" },
  ];
  renderStatCardGrid("distraction-stats", cards);
}

function renderBarChart(canvasId, series, { color }) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: series.labels,
      datasets: [{ data: series.values, backgroundColor: color, borderRadius: 6, maxBarThickness: 36 }],
    },
    options: chartOptionsBase,
  });
}

function renderLineChart(canvasId, series, { borderColor, fillColor }) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: "line",
    data: {
      labels: series.labels,
      datasets: [{
        data: series.values,
        borderColor,
        backgroundColor: fillColor,
        tension: 0.35,
        fill: true,
        spanGaps: false, // days with no sessions (null) show as a real gap, not a false 0
        pointBackgroundColor: "#0B0E1A",
        pointBorderColor: borderColor,
        pointBorderWidth: 2,
        pointRadius: 4,
      }],
    },
    options: {
      ...chartOptionsBase,
      scales: { ...chartOptionsBase.scales, y: { ...chartOptionsBase.scales.y, min: 0, max: 100 } },
    },
  });
}

async function loadAnalytics() {
  try {
    const res = await fetch(ANALYTICS_API_URL);
    if (!res.ok) throw new Error(`Server responded ${res.status}`);
    const data = await res.json();

    renderStatCards(data.distraction_stats);
    renderBarChart("study-hours-chart", data.daily_study_hours, { color: "#7C6CFF" });
    renderLineChart("focus-trend-chart", data.focus_trend, { borderColor: "#4CC9F0", fillColor: "rgba(76,201,240,0.15)" });
    renderLineChart("productivity-trend-chart", data.productivity_trend, { borderColor: "#F5A623", fillColor: "rgba(245,166,35,0.15)" });
    renderBarChart("distractions-chart", data.distraction_per_day, { color: "#FF6B6B" });

    if (data.distraction_stats.sessions_logged === 0) {
      document.getElementById("analytics-empty-note").classList.remove("hidden");
    }
  } catch (err) {
    console.error("Failed to load analytics:", err);
    showErrorBanner("Couldn't load analytics data. Check that the backend is running and try refreshing.");
  }
}

loadAnalytics();
