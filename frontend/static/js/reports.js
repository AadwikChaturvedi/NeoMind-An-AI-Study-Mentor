// reports.js — fetches the real report summary from GET /reports/summary
// and renders it. The PDF download itself is just a plain link
// (/reports/pdf) in reports.html — no JS needed for that part, the
// browser handles the download via the Content-Disposition header.

const REPORT_API_URL = "/reports/summary";

function renderStatCards(summary) {
  const cards = [
    { label: "Total study hours", value: `${summary.total_study_hours}h`, accent: "violet" },
    { label: "Average focus score", value: summary.average_focus_score, accent: "cyan" },
    { label: "Distractions this week", value: summary.distractions_this_week, accent: "coral" },
    { label: "Sessions logged", value: summary.sessions_logged, accent: "amber" },
  ];
  renderStatCardGrid("report-stats", cards);
}

function renderProductivitySummary(summary) {
  const el = document.getElementById("productivity-summary");
  if (summary.sessions_logged === 0) {
    el.textContent = "No sessions yet — this will fill in once you've logged some study time.";
    return;
  }
  el.textContent =
    `Your average productivity score is ${summary.average_productivity_score}/100, based on ` +
    `${summary.sessions_logged} logged session${summary.sessions_logged === 1 ? "" : "s"}. ` +
    `This score factors your focus score in with logged distractions — it isn't a raw measurement, ` +
    `just a useful way to see focus and distractions together at a glance.`;
}

async function loadReport() {
  try {
    const res = await fetch(REPORT_API_URL);
    if (!res.ok) throw new Error(`Server responded ${res.status}`);
    const summary = await res.json();

    renderStatCards(summary);
    renderProductivitySummary(summary);

    if (summary.sessions_logged === 0) {
      document.getElementById("reports-empty-note").classList.remove("hidden");
    }
  } catch (err) {
    console.error("Failed to load report:", err);
    showErrorBanner("Couldn't load the report. Check that the backend is running and try refreshing.");
  }
}

loadReport();
