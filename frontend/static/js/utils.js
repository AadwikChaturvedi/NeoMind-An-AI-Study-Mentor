// utils.js — small helpers shared across page scripts (dashboard.js,
// analytics.js, reports.js). Loaded once in base.html, before each
// page's own script, so every page can call these directly.

/**
 * Renders a grid of stat cards into the given container.
 * Each card: { label, value, accent, sub? } — `sub` is optional, an
 * extra descriptive line under the value (dashboard uses this; the
 * simpler analytics/reports cards don't need it).
 */
function renderStatCardGrid(containerId, cards) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = cards.map(c => `
    <div class="rounded-2xl border border-hairline bg-surface p-5">
      <p class="text-xs text-ink2 mb-2">${c.label}</p>
      <p class="font-mono text-2xl text-${c.accent}">${c.value}</p>
      ${c.sub ? `<p class="text-xs text-ink2 mt-2">${c.sub}</p>` : ""}
    </div>
  `).join("");
}

/**
 * Shows an error banner at the top of <main>. Used when a page's
 * initial data fetch fails, so every page fails the same way instead
 * of each one inventing its own error UI.
 */
function showErrorBanner(message) {
  document.querySelector("main")?.insertAdjacentHTML(
    "afterbegin",
    `<div class="rounded-2xl border border-coral/40 bg-coral/10 text-coral text-sm px-4 py-3 mb-6">
      ${message}
    </div>`
  );
}
