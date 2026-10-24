document.querySelectorAll('[data-upload-form]').forEach(form => {
  if (!window.XMLHttpRequest || !window.FormData) return;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('button[type=submit]');
    const status = form.querySelector('.studio-save');
    const progress = form.querySelector('progress');
    const xhr = new XMLHttpRequest();
    button.disabled = true; progress.hidden = false;
    status.textContent = 'Cargando archivo…';
    try {
      if (window.btcAccountContext) await window.btcAccountContext(form);
    } catch {
      status.textContent = 'La sesión o cuenta cambió. Entra con esta cuenta en otra pestaña y reintenta; el archivo sigue seleccionado.';
      button.disabled = false; progress.hidden = true; return;
    }
    xhr.open('POST', form.action || window.location.href);
    xhr.setRequestHeader('X-Requested-With','XMLHttpRequest');
    xhr.upload.addEventListener('progress', event => { if (event.lengthComputable) progress.value = event.loaded / event.total * 100; });
    xhr.addEventListener('load', () => {
      if (xhr.status === 200 && !/\/(?:cuenta|crear)\/entrar\//.test(xhr.responseURL)) {
        if (xhr.getResponseHeader('Content-Type')?.includes('application/json')) {
          window.location.assign(JSON.parse(xhr.responseText).redirect); return;
        }
        // Validation errors are rendered by Django, with their complete labels.
        const page = new DOMParser().parseFromString(xhr.responseText, 'text/html');
        const errors = page.querySelector('.studio-error');
        if (!errors) { window.location.assign(xhr.responseURL); return; }
        form.querySelector('.studio-error')?.remove();
        form.prepend(errors);
        errors.scrollIntoView({block:'center'});
        status.textContent = 'Corrige el archivo y vuelve a intentarlo';
      } else {
        status.textContent = /\/(?:cuenta|crear)\/entrar\//.test(xhr.responseURL) ? 'Tu sesión venció. Abre Entrar en otra pestaña y reintenta; el archivo sigue seleccionado.' : 'No se pudo guardar. Conservamos tu selección para reintentar.';
      }
      button.disabled = false;
    });
    xhr.addEventListener('error', () => { status.textContent = 'Se perdió la conexión. Reintenta con el archivo seleccionado.'; button.disabled = false; });
    xhr.send(new FormData(form));
  });
});
