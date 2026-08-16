// dashboard.js — mock data only, no backend calls yet.

const stats = [
  { label: "Focus time today", value: "3h 42m", trend: "+18% vs yesterday", accent: "violet" },
  { label: "Avg focus score", value: "82", trend: "+4 pts this week", accent: "cyan" },
  { label: "Current streak", value: "6 days", trend: "Personal best: 11", accent: "amber" },
  { label: "Sessions this week", value: "14", trend: "3 subjects covered", accent: "coral" },
];

const recentSessions = [
  { subject: "Organic Chemistry", duration: "52m", focusScore: 88, distractions: 2, when: "2h ago" },
  { subject: "Linear Algebra", duration: "38m", focusScore: 74, distractions: 5, when: "5h ago" },
  { subject: "World History", duration: "61m", focusScore: 91, distractions: 1, when: "Yesterday" },
  { subject: "Spanish Vocabulary", duration: "24m", focusScore: 69, distractions: 6, when: "Yesterday" },
];

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

function renderSessions() {
  const el = document.getElementById("recent-sessions");
  el.innerHTML = recentSessions.map(s => `
    <div class="flex items-center justify-between py-3 first:pt-0 last:pb-0">
      <div>
        <p class="text-sm font-medium">${s.subject}</p>
        <p class="text-xs text-ink2">${s.duration} · ${s.distractions} distractions · ${s.when}</p>
      </div>
      <span class="font-mono text-sm ${s.focusScore >= 80 ? 'text-cyan' : s.focusScore >= 70 ? 'text-amber' : 'text-coral'}">${s.focusScore}</span>
    </div>
  `).join("");
}

greet();
renderStats();
renderSessions();
