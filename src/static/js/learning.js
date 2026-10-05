(() => {
  'use strict';
  const form = document.querySelector('[data-progress-form]');
  if (!form) return;
  const status = form.querySelector('[data-progress-status]');
  const revision = form.querySelector('[name="revision"]');
  const completion = form.querySelector('[data-completion]');
  const reload = form.querySelector('[data-progress-reload]');
  let queue = Promise.resolve();
  let conflicted = false;
  async function save(action) {
    if (conflicted) return;
    const body = new FormData(form);
    body.set('action', action);
    status.textContent = 'Guardando tu avance…';
    form.setAttribute('aria-busy', 'true');
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
      status.textContent = data.message;
      completion.value = data.is_completed ? 'incomplete' : 'complete';
      completion.textContent = data.is_completed ? 'Marcar como pendiente' : 'Marcar lección completada';
      document.querySelector('[data-progress-count]').textContent = `${data.completed} de ${data.total}`;
      const progress = document.querySelector('[data-course-progress]');
      progress.max = data.total;
      progress.value = data.completed;
    } catch (error) {
      status.textContent = error instanceof TypeError ? 'No pudimos conectar para guardar. Reintenta desde esta lección.' : error.message || 'No pudimos guardar. Reintenta desde esta lección.';
    } finally {
      form.removeAttribute('aria-busy');
    }
  }
  function enqueue(action) { queue = queue.then(() => save(action)); }
  form.addEventListener('submit', event => {
    event.preventDefault();
    enqueue(event.submitter?.value || 'position');
  });
  reload.addEventListener('click', () => window.location.reload());
  // Saves only the current lesson, never completion or playback duration.
  enqueue('position');
})();
