/* Run in the head so the chosen theme is applied before the page paints. */
(() => {
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const key = 'btc-edu-theme';
  let preference;
  try { preference = localStorage.getItem(key); } catch (_) { /* Storage is optional. */ }
  if (!['light', 'dark'].includes(preference)) preference = null;
  function apply(theme) {
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.hidden = false;
      button.setAttribute('aria-pressed', String(theme === 'dark'));
      button.setAttribute('aria-label', theme === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro');
      button.textContent = theme === 'dark' ? '☀ Claro' : '☾ Oscuro';
    });
  }
  const refresh = () => apply(preference || (system.matches ? 'dark' : 'light'));
  refresh();
  document.addEventListener('DOMContentLoaded', refresh);
  document.addEventListener('click', event => {
    if (!event.target.closest('[data-theme-toggle]')) return;
    preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(key, preference); } catch (_) { /* Keep the choice for this page. */ }
    refresh();
  });
  system.addEventListener('change', () => { if (!preference) refresh(); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      preference = ['light', 'dark'].includes(event.newValue) ? event.newValue : null;
      refresh();
    }
  });
  document.addEventListener('htmx:afterSwap', refresh);
})();
