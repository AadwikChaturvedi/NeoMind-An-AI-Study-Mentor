// analytics.js — mock analytics rendered with hand-built SVG/CSS charts (no chart library).

const subjectMinutes = [
  { subject: "Organic Chemistry", minutes: 186 },
  { subject: "Linear Algebra", minutes: 142 },
  { subject: "World History", minutes: 98 },
  { subject: "Spanish Vocabulary", minutes: 64 },
];

const focusTrend = [74, 81, 69, 88, 91, 77, 85]; // last 7 sessions

const distractionBreakdown = [
  { label: "Phone notifications", count: 18, accent: "coral" },
  { label: "Social media", count: 11, accent: "amber" },
  { label: "Noise / people", count: 7, accent: "violet" },
  { label: "Other tabs open", count: 9, accent: "cyan" },
];

function renderSubjectChart() {
  const max = Math.max(...subjectMinutes.map(s => s.minutes));
  const el = document.getElementById("subject-chart");
  el.innerHTML = subjectMinutes.map(s => `
    <div class="mb-4 last:mb-0">
      <div class="flex justify-between text-xs mb-1.5">
        <span class="text-[#EDEEF7]">${s.subject}</span>
        <span class="font-mono text-ink2">${s.minutes}m</span>
      </div>
      <div class="h-2.5 rounded-full bg-elevated overflow-hidden">
        <div class="h-full rounded-full bg-gradient-to-r from-violet to-cyan" style="width:${(s.minutes / max) * 100}%"></div>
      </div>
    </div>
  `).join("");
}

function renderFocusTrend() {
  const el = document.getElementById("focus-trend");
  const w = 280, h = 120, pad = 10;
  const max = 100, min = 50;
  const points = focusTrend.map((v, i) => {
    const x = pad + (i * (w - pad * 2)) / (focusTrend.length - 1);
    const y = h - pad - ((v - min) / (max - min)) * (h - pad * 2);
    return [x, y];
  });
  const path = points.map((p, i) => (i === 0 ? "M" : "L") + p[0] + "," + p[1]).join(" ");
  const areaPath = path + ` L${points[points.length - 1][0]},${h - pad} L${points[0][0]},${h - pad} Z`;

  el.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" class="w-full h-32">
      <defs>
        <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#7C6CFF" stop-opacity="0.35" />
          <stop offset="100%" stop-color="#7C6CFF" stop-opacity="0" />
        </linearGradient>
      </defs>
      <path d="${areaPath}" fill="url(#trendFill)" />
      <path d="${path}" fill="none" stroke="#4CC9F0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      ${points.map(p => `<circle cx="${p[0]}" cy="${p[1]}" r="3" fill="#0B0E1A" stroke="#4CC9F0" stroke-width="2" />`).join("")}
    </svg>
    <div class="flex justify-between text-xs text-ink2 mt-2">
      <span>7 sessions ago</span><span>Latest</span>
    </div>
  `;
}

function renderDistractions() {
  const el = document.getElementById("distraction-list");
  el.innerHTML = distractionBreakdown.map(d => `
    <div class="rounded-2xl bg-surface border border-hairline p-4">
      <p class="font-mono text-2xl text-${d.accent}">${d.count}</p>
      <p class="text-xs text-ink2 mt-1">${d.label}</p>
    </div>
  `).join("");
}

renderSubjectChart();
renderFocusTrend();
renderDistractions();
