// dashboard.js — real data only, fetched from the backend.
// Reuses two endpoints that already exist rather than adding a new one:
//   /reports/summary   -> all-time totals for the 4 stat cards + streak
//   /analytics/summary -> today's hours specifically (last day in its
//                          7-day daily_study_hours series is always today)

function greet() {
  const hour = new Date().getHours();
  const part = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
  const el = document.getElementById("greeting-text");
  if (el) el.textContent = `Good ${part}, Aadwik.`;
}

function renderStatCards(report) {
  const cards = [
    { label: "Total study hours", value: `${report.total_study_hours}h`, sub: "All-time", accent: "violet" },
    { label: "Focus score", value: report.average_focus_score, sub: "Average across all sessions", accent: "cyan" },
    { label: "Study sessions", value: report.sessions_logged, sub: "All-time", accent: "amber" },
    { label: "Productivity index", value: report.average_productivity_score, sub: "Out of 100", accent: "coral" },
  ];
  renderStatCardGrid("stat-cards", cards);
}

function renderHero(report, todayHours) {
  const heroSubtext = document.getElementById("hero-subtext");
  const hours = Math.floor(todayHours);
  const minutes = Math.round((todayHours - hours) * 60);
  const todayLabel = todayHours > 0 ? `${hours}h ${minutes}m` : "0m";

  heroSubtext.innerHTML =
    `You've studied <span class="font-mono text-[#EDEEF7]">${todayLabel}</span> today. ` +
    `Your average focus score is <span class="font-mono text-[#EDEEF7]">${report.average_focus_score}</span> ` +
    `across ${report.sessions_logged} session${report.sessions_logged === 1 ? "" : "s"}.`;

  const streakEl = document.getElementById("hero-streak");
  const streakText = report.current_streak_days > 0
    ? `${report.current_streak_days}-day streak`
    : "Start your streak today";
  streakEl.innerHTML =
    `<span class="waveform"><span></span><span></span><span></span><span></span><span></span></span>${streakText}`;
}

function renderHighlights() {
  const highlights = [
    {
      title: "AI Mentor",
      desc: "Real Gemini-powered coaching that reads your actual session data — not canned tips.",
      icon: `<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>`,
      accent: "violet",
    },
    {
      title: "Study Timer",
      desc: "A focus timer that logs every session automatically the moment you stop it.",
      icon: `<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>`,
      accent: "cyan",
    },
    {
      title: "Real Analytics",
      desc: "Every chart in this app is built from your actual sessions — nothing here is a placeholder.",
      icon: `<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/><rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/>`,
      accent: "amber",
    },
    {
      title: "PDF Reports",
      desc: "Download a clean, printable summary of your progress in one click, anytime.",
      icon: `<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h6"/>`,
      accent: "coral",
    },
  ];

  document.getElementById("highlight-cards").innerHTML = highlights.map(h => `
    <div class="rounded-2xl border border-hairline bg-elevated p-5">
      <div class="h-9 w-9 rounded-lg bg-${h.accent}/15 text-${h.accent} flex items-center justify-center mb-3">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${h.icon}</svg>
      </div>
      <p class="font-display text-base mb-1">${h.title}</p>
      <p class="text-xs text-ink2 leading-relaxed">${h.desc}</p>
    </div>
  `).join("");
}

async function loadDashboard() {
  try {
    const [reportRes, analyticsRes] = await Promise.all([
      fetch("/reports/summary"),
      fetch("/analytics/summary"),
    ]);
    if (!reportRes.ok || !analyticsRes.ok) throw new Error("One or more requests failed");

    const report = await reportRes.json();
    const analytics = await analyticsRes.json();
    const todayHours = analytics.daily_study_hours.values.at(-1) ?? 0;

    renderStatCards(report);
    renderHero(report, todayHours);
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
    document.getElementById("hero-subtext").textContent =
      "Your progress will appear here once the backend is reachable.";
    showErrorBanner("Couldn't load your dashboard data. Check that the backend is running and try refreshing.");
  }
}

greet();
renderHighlights();
loadDashboard();
