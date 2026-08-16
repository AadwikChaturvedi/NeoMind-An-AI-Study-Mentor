// reports.js — mock saved reports, no backend calls.

const reports = [
  {
    title: "Week of Aug 4 – Aug 10",
    summary: "18h 40m studied across 4 subjects. Focus score averaged 82, up 6 points from the previous week.",
    focusScore: 82,
    minutes: 1120,
    date: "Aug 10, 2026",
  },
  {
    title: "Week of Jul 28 – Aug 3",
    summary: "14h 05m studied. Organic Chemistry sessions had the most distractions — mostly phone notifications.",
    focusScore: 76,
    minutes: 845,
    date: "Aug 3, 2026",
  },
  {
    title: "Week of Jul 21 – Jul 27",
    summary: "9h 50m studied, a lighter week. Mentor suggested shorter, more frequent sessions going forward.",
    focusScore: 71,
    minutes: 590,
    date: "Jul 27, 2026",
  },
];

function renderReports() {
  const el = document.getElementById("reports-list");
  el.innerHTML = reports.map(r => `
    <div class="rounded-2xl border border-hairline bg-surface p-6 flex flex-col lg:flex-row lg:items-center gap-4 lg:gap-8">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <h3 class="font-display text-lg">${r.title}</h3>
          <span class="text-xs text-ink2">${r.date}</span>
        </div>
        <p class="text-sm text-ink2 leading-relaxed">${r.summary}</p>
      </div>
      <div class="flex gap-6 lg:gap-8">
        <div>
          <p class="font-mono text-xl text-cyan">${Math.floor(r.minutes / 60)}h ${r.minutes % 60}m</p>
          <p class="text-xs text-ink2 mt-1">Studied</p>
        </div>
        <div>
          <p class="font-mono text-xl text-violet">${r.focusScore}</p>
          <p class="text-xs text-ink2 mt-1">Focus score</p>
        </div>
      </div>
      <button class="rounded-xl border border-hairline px-4 py-2.5 text-sm hover:bg-elevated transition whitespace-nowrap">View report</button>
    </div>
  `).join("");
}

renderReports();
