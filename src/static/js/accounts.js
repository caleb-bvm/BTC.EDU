window.btcAccountContext = async form => {
  const identity = form.querySelector('[name="account_id"]');
  if (!identity) return null;
  const response = await fetch('/cuenta/contexto/', {credentials:'same-origin',cache:'no-store'});
  if (!response.ok) throw new Error('account-session-changed');
  const current = await response.json();
  if (current.account_id !== identity.value) throw new Error('account-session-changed');
  form.querySelectorAll('[name="csrfmiddlewaretoken"]').forEach(input => { input.value = current.csrf_token; });
  return current;
};
document.querySelectorAll('[data-account-form]').forEach(form => {
  let dirty = false;
  const status = form.querySelector('[data-account-save]');
  form.addEventListener('input', () => { dirty = true; if (status) status.textContent = 'Cambios sin guardar'; });
  form.addEventListener('submit', async event => {
    if (!form.checkValidity()) return;
    if (form.hasAttribute('data-account-native') || !window.fetch) { dirty = false; return; }
    event.preventDefault();
    const button = form.querySelector('button[type="submit"],button:not([type])');
    if (button) { button.disabled = true; button.setAttribute('aria-busy', 'true'); }
    if (status) status.textContent = 'Guardando…';
    try {
      await window.btcAccountContext(form);
      const response = await fetch(form.action || window.location.href, {method:'POST',body:new FormData(form),credentials:'same-origin',headers:{'X-Requested-With':'XMLHttpRequest'}});
      if (!response.ok || /\/(?:cuenta|crear)\/entrar\//.test(response.url)) {
        if (status) status.textContent = response.status === 403 ? 'La sesión o cuenta cambió. Vuelve a entrar y reintenta; tus cambios siguen aquí.' : 'No se pudo guardar. Conservamos tus cambios para reintentar.';
        return;
      }
      if (response.headers.get('Content-Type')?.includes('application/json')) {
        const result = await response.json();
        dirty = false;
        window.location.assign(result.redirect);
        return;
      }
      const page = new DOMParser().parseFromString(await response.text(), 'text/html');
      const errors = page.querySelector('.account-errors');
      if (!errors) {
        if (status) status.textContent = 'No pudimos confirmar el guardado. Tus cambios siguen aquí; recarga tu cuenta en otra pestaña para comprobarlo.';
        return;
      }
      form.querySelector('.account-errors')?.remove();
      form.querySelectorAll('.errorlist').forEach(error => error.remove());
      form.querySelectorAll('[aria-invalid]').forEach(input => input.removeAttribute('aria-invalid'));
      form.prepend(errors);
      page.querySelectorAll('.account-field').forEach(field => {
        const input = field.querySelector('input,textarea,select');
        const target = input && form.querySelector(`#${input.id}`);
        const error = field.querySelector('.errorlist');
        if (target && error) {
          target.closest('.account-field').append(error);
          target.setAttribute('aria-invalid','true');
          if (error.id) target.setAttribute('aria-describedby', [...new Set([...(target.getAttribute('aria-describedby') || '').split(' ').filter(Boolean),error.id])].join(' '));
        }
      });
      errors.focus();
      if (status) status.textContent = 'Corrige los campos indicados y vuelve a guardar.';
    } catch (error) {
      if (status) status.textContent = error.message === 'account-session-changed' ? 'La sesión o cuenta cambió. Entra con esta cuenta en otra pestaña y vuelve a guardar; tus cambios siguen aquí.' : 'Se perdió la conexión. Tus cambios siguen aquí; vuelve a intentarlo cuando regrese.';
    } finally {
      if (button) { button.disabled = false; button.removeAttribute('aria-busy'); }
    }
  });
  window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
});
document.querySelectorAll('[data-avatar-form]').forEach(form => {
  const input = form.querySelector('[data-avatar-input]');
  const preview = form.querySelector('[data-avatar-preview]');
  const controls = form.querySelector('[data-avatar-crop]');
  const status = form.querySelector('[data-avatar-status]');
  let url = null;
  let dimensions = null;
  const updateCrop = () => {
    if (!dimensions) return;
    const zoom = Number(form.querySelector('[data-avatar-zoom]').value || 1);
    const edge = Math.min(dimensions.width, dimensions.height) / zoom;
    preview.style.backgroundSize = `${dimensions.width / edge * 100}% ${dimensions.height / edge * 100}%`;
    preview.style.backgroundPosition = `${form.querySelector('[data-avatar-x]').value}% ${form.querySelector('[data-avatar-y]').value}%`;
  };
  input.addEventListener('change', () => {
    const file = input.files?.[0];
    if (!file) return;
    if (file.size > 3 * 1024 * 1024 || !['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      status.textContent = 'Elige una foto JPG, PNG o WebP de hasta 3 MB.';
      input.value = '';
      return;
    }
    if (url) URL.revokeObjectURL(url);
    url = URL.createObjectURL(file);
    const photo = new Image();
    photo.onload = () => {
      dimensions = {width:photo.naturalWidth,height:photo.naturalHeight};
      preview.querySelector('.member-avatar').hidden = true;
      preview.style.backgroundImage = `url("${url}")`;
      controls.hidden = false;
      form.querySelector('[name="remove_photo"]')?.removeAttribute('checked');
      const remove = form.querySelector('[name="remove_photo"]'); if (remove) remove.checked = false;
      status.textContent = 'Ajusta la posición y el acercamiento. La vista previa muestra el recorte que se guardará.';
      updateCrop();
    };
    photo.onerror = () => { status.textContent = 'No pudimos leer la foto. Elige otro archivo.'; input.value = ''; };
    photo.src = url;
  });
  controls.addEventListener('input', updateCrop);
});
document.querySelectorAll('[data-profile-preview-form]').forEach(form => {
  const fields = ['display_name','bio','interests'];
  const update = () => fields.forEach(name => {
    const output = form.querySelector(`[data-preview-${name}]`);
    const input = form.querySelector(`[name="${name}"]`);
    if (output && input) output.textContent = input.value || (name === 'display_name' ? 'Participante' : '');
  });
  form.addEventListener('input', update);
  update();
});
document.querySelectorAll('.member-avatar img').forEach(photo => {
  photo.addEventListener('error', () => { photo.hidden = true; photo.parentElement.textContent = '＋'; });
});
