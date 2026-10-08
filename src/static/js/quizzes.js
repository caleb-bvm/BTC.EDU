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
    editor.querySelector(`[name="questions-${index}-prompt"]`).focus();
  });
});
