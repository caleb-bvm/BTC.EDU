document.querySelectorAll('[data-dirty-form]').forEach(form => {
  let dirty = false;
  const status = form.querySelector('.studio-save');
  form.addEventListener('input', () => { dirty = true; if (status) status.textContent = 'Cambios sin guardar'; });
  form.addEventListener('submit', async event => {
    if (!window.fetch || !window.FormData) { dirty = false; return; }
    event.preventDefault();
    const button = form.querySelector('button[type=submit]');
    button.disabled = true;
    if (status) status.textContent = 'Guardando…';
    try {
      const response = await fetch(form.action || window.location.href, {method:'POST', body:new FormData(form), credentials:'same-origin', headers:{'X-Requested-With':'XMLHttpRequest'}});
      if (response.url.includes('/cuenta/entrar/')) {
        if (status) status.textContent = 'Tu sesión venció. Abre Entrar en otra pestaña y reintenta; tus cambios siguen aquí.';
      } else if (response.ok) {
        if (response.headers.get('Content-Type')?.includes('application/json')) {
          const result = await response.json(); dirty = false; window.location.assign(result.redirect); return;
        }
        const page = new DOMParser().parseFromString(await response.text(), 'text/html');
        const errors = page.querySelector('.studio-error');
        if (!errors) { dirty = false; window.location.assign(response.url); return; }
        form.querySelector('.studio-error')?.remove();
        form.prepend(errors);
        form.querySelectorAll('.studio-field .errorlist').forEach(error => error.remove());
        page.querySelectorAll('.studio-field').forEach(field => {
          const input = field.querySelector('input,textarea,select');
          const target = input && form.querySelector(`#${input.id}`);
          const error = field.querySelector('.errorlist');
          if (target && error) {
            target.closest('.studio-field').append(error);
            if (error.id) target.setAttribute('aria-describedby', error.id);
            target.setAttribute('aria-invalid','true');
          }
        });
        errors.scrollIntoView({block:'center'});
        if (status) status.textContent = 'Corrige los campos indicados y vuelve a guardar';
      } else if (status) {
        status.textContent = response.status === 403 ? 'No se pudo autorizar el guardado. Abre Entrar en otra pestaña y reintenta; tus cambios siguen aquí.' : 'No se pudo guardar. Conservamos tus cambios para reintentar.';
      }
    } catch {
      if (status) status.textContent = 'Se perdió la conexión. Tus cambios siguen aquí; reintenta al recuperar conexión.';
    } finally { button.disabled = false; }
  });
  window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
});
document.querySelectorAll('[data-upload-form]').forEach(form => {
  if (!window.XMLHttpRequest || !window.FormData) return;
  form.addEventListener('submit', event => {
    event.preventDefault();
    const button = form.querySelector('button[type=submit]');
    const status = form.querySelector('.studio-save');
    const progress = form.querySelector('progress');
    const xhr = new XMLHttpRequest();
    button.disabled = true; progress.hidden = false;
    status.textContent = 'Cargando archivo…';
    xhr.open('POST', form.action || window.location.href);
    xhr.setRequestHeader('X-Requested-With','XMLHttpRequest');
    xhr.upload.addEventListener('progress', event => { if (event.lengthComputable) progress.value = event.loaded / event.total * 100; });
    xhr.addEventListener('load', () => {
      if (xhr.status === 200 && !xhr.responseURL.includes('/cuenta/entrar/')) {
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
        status.textContent = xhr.responseURL.includes('/cuenta/entrar/') ? 'Tu sesión venció. Abre Entrar en otra pestaña y reintenta; el archivo sigue seleccionado.' : 'No se pudo guardar. Conservamos tu selección para reintentar.';
      }
      button.disabled = false;
    });
    xhr.addEventListener('error', () => { status.textContent = 'Se perdió la conexión. Reintenta con el archivo seleccionado.'; button.disabled = false; });
    xhr.send(new FormData(form));
  });
});
