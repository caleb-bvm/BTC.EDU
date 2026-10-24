/* Shared authoring saves preserve values on validation, connection and session errors. */
(() => {
  const forms = new Set();
  function bind(form) {
    if (form.dataset.saveBound || form.hasAttribute('data-account-form') || form.hasAttribute('data-quiz-attempt')) return;
    form.dataset.saveBound = 'true';
    const accountId = document.querySelector('meta[name="btc-account-id"]')?.content;
    if (accountId && !form.querySelector('[name="account_id"]')) {
      const identity = document.createElement('input'); identity.type = 'hidden'; identity.name = 'account_id'; identity.value = accountId; form.append(identity);
    }
    let dirty = false, saving = false, revision = 0;
    let status = form.querySelector('.studio-save,[data-save-status],.form-save-status');
    if (!status) { status = document.createElement('p'); status.className = 'form-save-status'; form.append(status); }
    status.setAttribute('role','status'); status.textContent ||= 'Sin cambios pendientes';
    forms.add({dirty: () => dirty, connected: () => form.isConnected});
    const changed = () => { dirty = true; revision++; status.textContent = 'Cambios sin guardar'; };
    form.addEventListener('input',changed); form.addEventListener('change',changed);
    const reveal = target => {
      for (let parent = target.parentElement; parent && parent !== form; parent = parent.parentElement) if (parent.tagName === 'DETAILS') parent.open = true;
    };
    function showErrors(messages, page) {
      form.querySelector('.form-save-error')?.remove();
      form.querySelectorAll('.field-save-error').forEach(el => el.remove());
      form.querySelectorAll('[aria-invalid]').forEach(el => el.removeAttribute('aria-invalid'));
      const summary = document.createElement('div'); summary.className = 'form-save-error';
      summary.setAttribute('role','alert'); summary.tabIndex = -1;
      const title = document.createElement('p'); title.textContent = 'Revisa los campos indicados. Tus cambios siguen aquí.';
      const list = document.createElement('ul'); summary.append(title,list);
      const linked = new Set();
      if (page) page.querySelectorAll('details').forEach(section => {
        if (!section.querySelector('.errorlist')) return;
        const input = section.querySelector('input:not([type=hidden]),textarea,select');
        const target = input?.id && document.getElementById(input.id);
        if (target && form.contains(target)) reveal(target);
      });
      if (page) page.querySelectorAll('input,textarea,select').forEach(input => {
        const errorIds = (input.getAttribute('aria-describedby') || '').split(' ');
        const field = input.closest('.studio-field');
        const errors = errorIds.map(id => page.getElementById(id)).filter(el => el?.classList.contains('errorlist'));
        if (!errors.length && field?.querySelector('.errorlist')) errors.push(field.querySelector('.errorlist'));
        if (!errors.length) return;
        const target = input.id && document.getElementById(input.id);
        if (!target || !form.contains(target)) return;
        const label = ([...page.querySelectorAll('label')].find(el => el.getAttribute('for') === input.id)?.textContent.trim() || input.name).replace(/:\s*$/, '');
        const text = [...new Set(errors.map(el => el.textContent.trim()))].join(' ');
        const key = input.id + ':' + text;
        if (linked.has(key)) return; linked.add(key);
        const message = document.createElement('p'); message.className = 'field-save-error'; message.id = input.id + '_save_error'; message.textContent = text;
        const wrapper = target.closest('.studio-field');
        if (wrapper) wrapper.append(message); else target.after(message);
        target.setAttribute('aria-invalid','true');
        target.setAttribute('aria-describedby',[...new Set([...errorIds.filter(id => id && !id.endsWith('_save_error')),message.id])].join(' '));
        reveal(target);
        const item = document.createElement('li'), link = document.createElement('a');
        link.href = '#' + target.id; link.textContent = label + ': ' + text;
        link.addEventListener('click',event => { event.preventDefault(); reveal(target); target.focus(); });
        item.append(link); list.append(item);
      });
      [...new Set(messages)].forEach(text => {
        if ([...linked].some(key => key.endsWith(':' + text))) return;
        const item = document.createElement('li'); item.textContent = text; list.append(item);
      });
      form.prepend(summary); summary.focus(); status.textContent = 'Corrige los campos y vuelve a guardar.';
    }
    form.addEventListener('submit',async event => {
      if (event.defaultPrevented || !form.checkValidity()) return;
      if (!window.fetch || !window.FormData) { dirty = false; return; }
      event.preventDefault(); if (saving) return; saving = true;
      const sentRevision = revision;
      const button = event.submitter || form.querySelector('button[type=submit]');
      const body = new FormData(form); if (button?.name) body.append(button.name,button.value);
      const controls = [...form.querySelectorAll('input,textarea,select,button')].map(el => ({el,disabled:el.disabled}));
      controls.forEach(({el}) => { el.disabled = true; });
      button?.setAttribute('aria-busy','true'); status.textContent = 'Guardando…';
      const complete = destination => {
        if (new URL(destination,location.href).origin !== location.origin) throw new Error('save');
        if (revision !== sentRevision) { dirty = true; status.textContent = 'La versión enviada se guardó. Tus cambios posteriores siguen aquí; revisa el borrador antes de volver a guardar.'; return; }
        dirty = false; location.assign(destination);
      };
      try {
        if (window.btcAccountContext) await window.btcAccountContext(form);
        form.querySelectorAll('[name=csrfmiddlewaretoken]').forEach(input => body.set(input.name,input.value));
        const response = await fetch(form.action || location.href,{method:'POST',body,credentials:'same-origin',headers:{'X-Requested-With':'XMLHttpRequest'}});
        if (/\/(?:cuenta|crear)\/entrar\//.test(response.url) || response.status === 403) throw new Error('session');
        if (response.headers.get('Content-Type')?.includes('application/json')) {
          const result = await response.json();
          if (result.errors || result.error) { showErrors(result.errors || [result.error]); return; }
          if (!response.ok || !result.redirect || new URL(result.redirect,location.href).origin !== location.origin) throw new Error('save');
          complete(result.redirect); return;
        }
        const page = new DOMParser().parseFromString(await response.text(),'text/html');
        const errors = [...page.querySelectorAll('.errorlist,.studio-error,.form-error,[data-message-level~="error"]')].filter(el => el.textContent.trim() && !el.hasAttribute('data-field-error-summary'));
        if (errors.length) { showErrors(errors.map(el => el.textContent.trim()),page); return; }
        if (!response.ok || !response.redirected) throw new Error('unconfirmed');
        complete(response.url);
      } catch (error) {
        status.textContent = error.message === 'session' || error.message === 'account-session-changed'
          ? 'Tu sesión o cuenta cambió. Entra en otra pestaña y reintenta; tus cambios siguen aquí.'
          : 'No pudimos confirmar el guardado. Tus cambios siguen aquí; vuelve a intentarlo.';
      } finally {
        saving = false; controls.forEach(({el,disabled}) => { el.disabled = disabled; });
        button?.removeAttribute('aria-busy');
      }
    });
  }
  document.querySelectorAll('[data-dirty-form]').forEach(bind);
  document.addEventListener('htmx:afterSwap',event => event.detail.target.querySelectorAll('[data-dirty-form]').forEach(bind));
  window.addEventListener('beforeunload',event => { if ([...forms].some(form => form.connected() && form.dirty())) { event.preventDefault(); event.returnValue = ''; } });
})();
