(() => {
  'use strict';
  // A shared conversation or material remains reachable from its direct link.
  const revealAnchor = hash => {
    let id;
    try { id = decodeURIComponent(hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target) return;
    let disclosure = target.closest('details');
    while (disclosure) {
      disclosure.open = true;
      disclosure = disclosure.parentElement?.closest('details');
    }
  };
  revealAnchor(window.location.hash);
  window.addEventListener('hashchange', () => revealAnchor(window.location.hash));
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link) revealAnchor(link.hash);
  });
  const focusButton = document.querySelector('[data-reader-focus]');
  if (focusButton) {
    const focusReading = enabled => {
      document.body.classList.toggle('reader-focused', enabled);
      focusButton.setAttribute('aria-pressed', String(enabled));
      focusButton.textContent = enabled ? 'Salir de lectura enfocada ↙' : 'Enfocar lectura ↗';
    };
    focusButton.addEventListener('click', () => focusReading(focusButton.getAttribute('aria-pressed') !== 'true'));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && document.body.classList.contains('reader-focused')) {
        focusReading(false);
        focusButton.focus({preventScroll: true});
      }
    });
  }
  const outline = document.querySelector('.reader-outline');
  if (outline) {
    const compact = window.matchMedia('(max-width: 1100px)');
    outline.open = !compact.matches;
    compact.addEventListener('change', event => { outline.open = !event.matches; });
  }
  const form = document.querySelector('[data-progress-form]');
  if (!form) return;
  const status = form.querySelector('[data-progress-status]');
  const revision = form.querySelector('[name="revision"]');
  const completion = form.querySelector('[data-completion]');
  const reload = form.querySelector('[data-progress-reload]');
  const retry = form.querySelector('[data-progress-retry]');
  const quizBlocked = completion.disabled;
  const recordId = form.querySelector('[name="lesson"]').value;
  let busy = false;
  let conflicted = false;

  async function save(action) {
    if (conflicted || busy) return;
    busy = true;
    const body = new FormData(form);
    body.set('action', action);
    const explicit = action !== 'position';
    const recovering = status.classList.contains('save-error');
    if (explicit || recovering) status.textContent = 'Guardando tu avance…';
    form.setAttribute('aria-busy', 'true');
    completion.disabled = true;
    retry.disabled = true;
    try {
      const response = await fetch(form.getAttribute('action'), {method: 'POST', body, credentials: 'same-origin', headers: {'Accept': 'application/json'}, cache: 'no-store'});
      if (response.redirected) throw new Error('Tu sesión cambió. Vuelve a entrar para guardar el avance.');
      if (!response.headers.get('Content-Type')?.includes('application/json')) throw new Error('No pudimos guardar. Comprueba tu sesión y vuelve a intentarlo.');
      const data = await response.json();
      if (!response.ok || !data.saved) {
        if (response.status === 409) { conflicted = true; reload.hidden = false; }
        throw new Error(data.message || 'No pudimos guardar. Reintenta desde esta lección.');
      }
      revision.value = data.revision;
      retry.hidden = true;
      if (explicit || recovering) status.textContent = data.message;
      status.classList.remove('save-error');
      completion.value = data.is_completed ? 'incomplete' : 'complete';
      completion.textContent = data.is_completed ? 'Marcar como pendiente' : 'Marcar lección completada';
      completion.classList.toggle('btn-dark', !data.is_completed);
      completion.classList.toggle('btn-outline-dark', data.is_completed);
      const continueLink = document.querySelector('[data-completion-next]');
      if (continueLink) continueLink.hidden = !data.is_completed;
      const percentage = data.total ? Math.round(data.completed * 100 / data.total) : 0;
      document.querySelectorAll('[data-progress-count]').forEach(item => { item.textContent = `${data.completed} de ${data.total}`; });
      document.querySelectorAll('[data-progress-percentage]').forEach(item => { item.textContent = `${percentage}%`; });
      document.querySelectorAll('[data-course-progress]').forEach(item => { item.max = data.total || 1; item.value = data.completed; });
      document.querySelectorAll(`[data-outline-lesson="${recordId}"]`).forEach(item => {
        item.closest('li').classList.toggle('is-complete', data.is_completed);
        item.querySelector('[data-lesson-marker]').textContent = data.is_completed ? '✓' : String(document.querySelector('.reader-toolbar strong').textContent).padStart(2, '0');
        const state = item.querySelector('[data-lesson-state]');
        state.textContent = data.is_completed ? 'Completada' : 'Estás aquí';
        state.classList.toggle('state-complete', data.is_completed);
      });
      const currentState = document.querySelector('[data-current-lesson-state]');
      currentState.textContent = data.is_completed ? 'Completada' : 'Por estudiar';
      currentState.classList.toggle('state-complete', data.is_completed);
      document.querySelector('[data-completion-heading]').textContent = data.is_completed ? 'Una lección más en tu recorrido.' : '¿Terminaste esta lección?';
      document.querySelector('[data-course-finished]').hidden = !(data.total > 0 && data.completed === data.total);
    } catch (error) {
      retry.hidden = conflicted;
      status.textContent = error instanceof TypeError ? 'No pudimos conectar para guardar. Reintenta desde esta lección.' : error.message || 'No pudimos guardar. Reintenta desde esta lección.';
      status.classList.add('save-error');
    } finally {
      busy = false;
      form.removeAttribute('aria-busy');
      completion.disabled = conflicted || quizBlocked;
      retry.disabled = conflicted;
    }
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    save(event.submitter?.value || 'position');
  });
  reload.addEventListener('click', () => window.location.reload());
  // Opening remembers the lesson; completion remains an explicit student action.
  save('position');
})();
