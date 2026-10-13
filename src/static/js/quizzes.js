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
  const steps = form.querySelector('[data-step-actions]');
  const previous = form.querySelector('[data-previous-question]');
  const next = form.querySelector('[data-next-question]');
  const review = form.querySelector('[data-submit-review]');
  const confirm = form.querySelector('[data-confirm-submit]');
  let current = 0;
  let reviewing = false;
  let dirty = false;
  let leaving = false;
  const selected = (question) => [...question.querySelectorAll('input:checked')];
  const answered = (question) => selected(question).length > 0;
  const labels = (question) => selected(question).map(input => input.closest('label').textContent.trim());
  const buttons = questions.map((question, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.addEventListener('click', () => show(index));
    navigation.append(button);
    return button;
  });
  function update() {
    const count = questions.filter(answered).length;
    form.querySelector('[data-quiz-progress]').textContent = count + ' de ' + questions.length + ' respondidas';
    form.querySelector('[data-quiz-meter]').value = count;
    buttons.forEach((button, index) => {
      const done = answered(questions[index]);
      button.textContent = String(index + 1) + (done ? ' ✓' : '');
      button.classList.toggle('is-answered', done);
      button.setAttribute('aria-label', 'Pregunta ' + (index + 1) + ', ' + (done ? 'respondida' : 'sin responder'));
      if (index === current && !reviewing) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
    });
    previous.disabled = current === 0;
    next.textContent = current === questions.length - 1 ? 'Revisar respuestas →' : 'Siguiente →';
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
    form.querySelector('[data-submit-summary]').textContent = pending
      ? 'Quedan ' + pending + ' preguntas sin responder. Complétalas para entregar.'
      : 'Respondiste todas las preguntas. Puedes cambiar cualquier respuesta o entregar el intento.';
    const summary = form.querySelector('[data-answer-summary]');
    summary.replaceChildren();
    questions.forEach((question, index) => {
      const row = document.createElement('div');
      row.className = 'assessment-summary-row';
      const copy = document.createElement('div');
      const title = document.createElement('h3');
      title.textContent = question.querySelector('legend').textContent.trim().replace(/(Pregunta \d+ de \d+)/, '$1 · ');
      const answers = document.createElement('p');
      answers.textContent = labels(question).join('\n') || 'Sin responder';
      const edit = document.createElement('button');
      edit.type = 'button';
      edit.textContent = answered(question) ? 'Cambiar' : 'Responder';
      edit.setAttribute('aria-label', edit.textContent + ' pregunta ' + (index + 1));
      edit.addEventListener('click', () => show(index));
      copy.append(title, answers);
      row.append(copy, edit);
      summary.append(row);
    });
    update();
    review.focus();
  }
  previous.addEventListener('click', () => show(Math.max(0, current - 1)));
  next.addEventListener('click', () => current < questions.length - 1 ? show(current + 1) : showReview());
  form.querySelector('[data-back-to-questions]').addEventListener('click', () => show(current));
  form.addEventListener('change', () => {
    dirty = true;
    form.querySelector('[data-save-status]').textContent = 'Tienes cambios sin guardar.';
    update();
  });
  form.addEventListener('submit', (event) => {
    // Save remains available at every step; only final submission uses the review.
    if (event.submitter?.value === 'submit' && (!reviewing || questions.some(question => !answered(question)))) {
      event.preventDefault();
      showReview();
      return;
    }
    leaving = true;
  });
  window.addEventListener('beforeunload', (event) => {
    if (dirty && !leaving) { event.preventDefault(); event.returnValue = ''; }
  });
  map.hidden = false;
  form.querySelector('[data-fallback-submit]').hidden = true;
  const errorIndex = questions.findIndex(question => question.querySelector('.errorlist'));
  const firstPending = questions.findIndex(question => !answered(question));
  show(errorIndex >= 0 ? errorIndex : firstPending >= 0 ? firstPending : 0, false);
  const errors = form.querySelector('[data-attempt-errors]');
  if (errors) errors.focus();
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
