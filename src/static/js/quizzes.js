document.querySelectorAll('[data-quiz-editor]').forEach((editor) => {
  const button = editor.querySelector('[data-add-question]');
  const total = editor.querySelector('[name="questions-TOTAL_FORMS"]');
  button.hidden = false;
  button.addEventListener('click', () => {
    const index = Number(total.value);
    if (index >= 20) {
      editor.querySelector('[data-question-status]').textContent = 'El máximo es 20 preguntas. Puedes editar o eliminar las existentes.';
      return;
    }
    const wrapper = document.createElement('div');
    wrapper.innerHTML = editor.querySelector('[data-question-template]').innerHTML.replaceAll('__prefix__', String(index));
    editor.querySelector('[data-question-list]').append(...wrapper.children);
    total.value = String(index + 1);
    editor.dispatchEvent(new Event('input', {bubbles: true}));
    const added = editor.querySelector(`[name="questions-${index}-prompt"]`).closest('details');
    if (added) {
      added.open = true;
      added.querySelector('.assessment-number').textContent = String(index + 1);
    }
    editor.querySelector(`[name="questions-${index}-prompt"]`).focus();
  });
});

document.querySelectorAll('[data-quiz-attempt]').forEach((form) => {
  const questions = [...form.querySelectorAll('[data-quiz-question]')];
  if (!questions.length) return;
  const map = form.querySelector('[data-quiz-map]');
  const navigation = form.querySelector('[data-question-navigation]');
  const toolbar = form.querySelector('[data-quiz-toolbar]');
  const track = form.querySelector('[data-quiz-track]');
  const steps = form.querySelector('[data-step-actions]');
  const previous = form.querySelector('[data-previous-question]');
  const next = form.querySelector('[data-next-question]');
  const flag = form.querySelector('[data-flag-question]');
  const review = form.querySelector('[data-submit-review]');
  const confirm = form.querySelector('[data-confirm-submit]');
  const saveStatus = form.querySelector('[data-save-status]');
  const saveError = form.querySelector('[data-save-error]');
  const revision = form.querySelector('[name="revision"]');
  // Flags are a personal reading aid: they stay in this browser and never reach the server.
  const flagKey = 'btc-edu-quiz-flags:' + location.pathname;
  let flags = new Set();
  try { flags = new Set(JSON.parse(localStorage.getItem(flagKey) || '[]')); } catch (error) { flags = new Set(); }
  let current = 0;
  let reviewing = false;
  let dirty = false;
  let saving = null;
  let timer = null;
  let leaving = false;
  const selected = (question) => [...question.querySelectorAll('input:checked')];
  const answered = (question) => selected(question).length > 0;
  const labels = (question) => selected(question).map(input => input.closest('label').textContent.trim());
  const prompt = (question) => [...question.querySelector('legend').childNodes].filter(node => !node.classList?.contains('quiz-question-caption')).map(node => node.textContent).join('').trim();
  const cell = () => document.createElement('i');
  const segments = questions.map(() => track.appendChild(cell()));
  const buttons = questions.map((question, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = String(index + 1);
    button.addEventListener('click', () => show(index));
    navigation.append(button);
    return button;
  });

  function storeFlags() {
    try { localStorage.setItem(flagKey, JSON.stringify([...flags])); } catch (error) { /* Flags still work for this visit. */ }
  }
  function update() {
    const count = questions.filter(answered).length;
    form.querySelector('[data-quiz-progress]').textContent = (reviewing ? 'Resumen' : 'Pregunta ' + (current + 1) + ' de ' + questions.length) + ' · ' + count + ' respondidas';
    questions.forEach((question, index) => {
      const done = answered(question);
      const marked = flags.has(index);
      const active = index === current && !reviewing;
      for (const item of [buttons[index], segments[index]]) {
        item.classList.toggle('is-answered', done);
        item.classList.toggle('is-flagged', marked);
        item.classList.toggle('is-current', active);
      }
      buttons[index].setAttribute('aria-label', 'Pregunta ' + (index + 1) + ', ' + (done ? 'respondida' : 'sin responder') + (marked ? ', marcada para revisar' : ''));
      if (active) buttons[index].setAttribute('aria-current', 'step');
      else buttons[index].removeAttribute('aria-current');
      question.querySelector('[data-flag-tag]').hidden = !marked;
    });
    const marked = flags.has(current);
    flag.setAttribute('aria-pressed', String(marked));
    flag.textContent = marked ? 'Marcada para revisar' : 'Marcar para revisar';
    previous.disabled = current === 0;
    next.textContent = current === questions.length - 1 ? 'Revisar y entregar →' : 'Siguiente →';
    confirm.disabled = count !== questions.length;
  }
  function show(index, focus = true) {
    current = index;
    reviewing = false;
    questions.forEach((question, i) => { question.hidden = i !== index; });
    review.hidden = true;
    steps.hidden = false;
    update();
    if (focus) questions[index].querySelector('legend').focus();
  }
  function showReview() {
    reviewing = true;
    questions.forEach(question => { question.hidden = true; });
    review.hidden = false;
    steps.hidden = true;
    const pending = questions.filter(question => !answered(question)).length;
    form.querySelector('[data-count-answered]').textContent = String(questions.length - pending);
    form.querySelector('[data-count-pending]').textContent = String(pending);
    form.querySelector('[data-count-flagged]').textContent = String(flags.size);
    form.querySelector('[data-submit-summary]').textContent = pending
      ? 'Responde ' + (pending === 1 ? 'la pregunta pendiente' : 'las ' + pending + ' preguntas pendientes') + ' para entregar.'
      : flags.size ? 'Respondiste todo. Revisa las preguntas marcadas si quieres cambiar algo.' : 'Respondiste todas las preguntas. Puedes cambiar cualquier respuesta o entregar el intento.';
    const summary = form.querySelector('[data-answer-summary]');
    summary.replaceChildren();
    questions.forEach((question, index) => {
      const row = document.createElement('div');
      row.className = 'quiz-summary-row' + (answered(question) ? '' : ' is-pending') + (flags.has(index) ? ' is-flagged' : '');
      const number = document.createElement('span');
      number.className = 'quiz-number';
      number.textContent = String(index + 1).padStart(2, '0');
      const copy = document.createElement('div');
      const title = document.createElement('h3');
      title.textContent = prompt(question);
      const answers = document.createElement('p');
      answers.textContent = labels(question).join('\n') || 'Sin responder';
      copy.append(title, answers);
      if (flags.has(index)) {
        const tag = document.createElement('span');
        tag.className = 'quiz-flag-tag';
        tag.textContent = 'Marcada';
        copy.prepend(tag);
      }
      const edit = document.createElement('button');
      edit.type = 'button';
      edit.textContent = answered(question) ? 'Cambiar' : 'Responder';
      edit.setAttribute('aria-label', edit.textContent + ' la pregunta ' + (index + 1));
      edit.addEventListener('click', () => show(index));
      row.append(number, copy, edit);
      summary.append(row);
    });
    update();
    review.focus();
  }
  function toggleFlag() {
    if (flags.has(current)) flags.delete(current);
    else flags.add(current);
    storeFlags();
    update();
  }

  // Answers save in the background; the page speaks only when a save needs the student.
  function setStatus(text) { saveStatus.textContent = text; }
  function fail(text, retry) {
    setStatus('Sin guardar');
    saveError.querySelector('[data-save-error-text]').textContent = text;
    saveError.querySelector('[data-save-retry]').hidden = !retry;
    saveError.hidden = false;
    saveError.focus();
  }
  async function save() {
    clearTimeout(timer);
    if (saving) return saving;
    if (!dirty) return true;
    dirty = false;
    setStatus('Guardando…');
    const body = new FormData(form);
    body.set('action', 'save');
    saving = fetch(location.href, {method: 'POST', body, credentials: 'same-origin', headers: {'X-Requested-With': 'XMLHttpRequest', Accept: 'application/json'}})
      .then(async (response) => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
          dirty = true;
          // A stale revision needs a reload; other server errors may pass on a retry.
          fail((data.errors || []).join(' ') || 'Recarga el intento para recuperar las respuestas guardadas.', response.status !== 409);
          return false;
        }
        revision.value = data.revision;
        saveError.hidden = true;
        setStatus(dirty ? 'Guardando…' : 'Guardado');
        return true;
      })
      .catch(() => {
        dirty = true;
        fail('Revisa tu conexión. Tus respuestas siguen en esta página.', true);
        return false;
      })
      .finally(() => { saving = null; });
    const result = await saving;
    if (result && dirty) return save();
    return result;
  }
  async function flush() {
    while (saving || dirty) {
      if ((await (saving || save())) === false) return false;
    }
    return true;
  }
  function schedule() {
    dirty = true;
    setStatus('Cambios sin guardar');
    clearTimeout(timer);
    timer = setTimeout(save, 700);
  }

  previous.addEventListener('click', () => show(Math.max(0, current - 1)));
  next.addEventListener('click', () => current < questions.length - 1 ? show(current + 1) : showReview());
  flag.addEventListener('click', toggleFlag);
  form.querySelector('[data-open-review]').addEventListener('click', showReview);
  form.querySelector('[data-back-to-questions]').addEventListener('click', () => show(current));
  form.querySelector('[data-save-retry]').addEventListener('click', () => { dirty = true; save(); });
  form.addEventListener('change', () => { update(); schedule(); });
  form.addEventListener('submit', async (event) => {
    if (leaving) return;
    event.preventDefault();
    if (event.submitter?.value !== 'submit' || !reviewing || questions.some(question => !answered(question))) {
      showReview();
      return;
    }
    confirm.disabled = true;
    // Submit with the latest revision so a background save never makes the delivery stale.
    if (!(await flush())) {
      confirm.disabled = false;
      return;
    }
    const action = document.createElement('input');
    action.type = 'hidden';
    action.name = 'action';
    action.value = 'submit';
    form.append(action);
    leaving = true;
    try { localStorage.removeItem(flagKey); } catch (error) { /* Nothing to clean. */ }
    form.submit();
  });
  document.addEventListener('keydown', (event) => {
    if (reviewing || event.altKey || event.ctrlKey || event.metaKey || event.target.closest('textarea, select, input[type=text], summary, a')) return;
    const choice = /^[1-6]$/.test(event.key) ? Number(event.key) - 1 : -1;
    const inputs = [...questions[current].querySelectorAll('input')];
    if (choice >= 0 && inputs[choice]) {
      event.preventDefault();
      inputs[choice].click();
      inputs[choice].focus();
    } else if (event.key.toLowerCase() === 'm') {
      event.preventDefault();
      toggleFlag();
    } else if ((event.key === 'ArrowRight' || event.key === 'ArrowLeft') && !event.target.matches('input')) {
      event.preventDefault();
      if (event.key === 'ArrowLeft') show(Math.max(0, current - 1));
      else if (current < questions.length - 1) show(current + 1);
      else showReview();
    }
  });
  window.addEventListener('beforeunload', (event) => {
    if ((dirty || saving) && !leaving) { event.preventDefault(); event.returnValue = ''; }
  });
  map.hidden = false;
  toolbar.hidden = false;
  form.querySelector('[data-save-bar]').hidden = true;
  setStatus('Guardado');
  const errorIndex = questions.findIndex(question => question.querySelector('.errorlist'));
  const firstPending = questions.findIndex(question => !answered(question));
  show(errorIndex >= 0 ? errorIndex : firstPending >= 0 ? firstPending : 0, false);
  const errors = form.querySelector('[data-attempt-errors]');
  if (errors) errors.focus();
});

document.querySelectorAll('[data-quiz-review]').forEach((section) => {
  const filters = section.querySelector('[data-review-filters]');
  if (!filters) return;
  const items = [...section.querySelectorAll('[data-review-item]')];
  filters.hidden = false;
  filters.addEventListener('click', (event) => {
    const button = event.target.closest('[data-review-filter]');
    if (!button || button.disabled) return;
    filters.querySelectorAll('[data-review-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    const value = button.dataset.reviewFilter;
    items.forEach((item) => { item.hidden = value !== 'all' && item.dataset.reviewItem !== value; });
  });
});

document.querySelectorAll('[data-quiz-editor]').forEach((editor) => {
  editor.addEventListener('input', (event) => {
    if (!event.target.name?.endsWith('-prompt')) return;
    const title = event.target.closest('details')?.querySelector('[data-question-title]');
    if (title) title.textContent = event.target.value.trim() || 'Nueva pregunta';
  });
  editor.addEventListener('invalid', (event) => {
    const section = event.target.closest('details');
    if (section) section.open = true;
  }, true);
});
