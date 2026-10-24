/* Adding to a cart keeps discovery in place; payment still needs explicit review. */
(() => {
  const bind = form => {
    if (form.dataset.cartBound || !window.fetch || !window.FormData) return;
    form.dataset.cartBound = 'true';
    let busy = false;
    const feedback = form.querySelector('[data-cart-feedback]') || form.parentElement.querySelector('[data-cart-feedback]');
    const button = form.querySelector('button[type=submit],button:not([type])');
    form.addEventListener('submit', async event => {
      if (!form.checkValidity() || event.defaultPrevented) return;
      event.preventDefault();
      if (busy) return;
      busy = true;
      const previous = button?.textContent;
      if (button) { button.disabled = true; button.textContent = 'Añadiendo…'; }
      form.setAttribute('aria-busy', 'true');
      try {
        if (window.btcAccountContext) await window.btcAccountContext(form);
        const body = new FormData(form);
        if (event.submitter?.name) body.append(event.submitter.name, event.submitter.value);
        const response = await fetch(form.action, {method: 'POST', body, credentials: 'same-origin',
          headers: {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}});
        if (response.redirected || !response.headers.get('Content-Type')?.includes('application/json')) throw new Error('session');
        const result = await response.json();
        if (!response.ok || !result.ok) throw new Error(result.message || 'No pudimos añadir esta selección. Revisa la opción y vuelve a intentar.');
        document.querySelectorAll('[data-cart-count]').forEach(count => { count.textContent = String(result.cart_count); count.hidden = result.cart_count <= 0; });
        document.querySelectorAll('[data-cart-link]').forEach(link => { link.setAttribute('aria-label', 'Carrito, ' + result.cart_count + (result.cart_count === 1 ? ' artículo' : ' artículos')); });
        if (feedback) { feedback.hidden = false; feedback.setAttribute('role', 'status'); feedback.textContent = result.message; }
      } catch (error) {
        if (feedback) {
          feedback.hidden = false;
          feedback.setAttribute('role', 'alert');
          feedback.textContent = error.message === 'session' || error.message === 'account-session-changed'
            ? 'La sesión cambió. Revisa tu cuenta en otra pestaña y vuelve a intentar.'
            : error instanceof TypeError ? 'No pudimos conectar. Conservamos tu selección; vuelve a intentar añadirla.'
            : error.message;
        }
      } finally {
        busy = false; form.removeAttribute('aria-busy');
        if (button) { button.disabled = false; button.textContent = previous; }
      }
    });
  };
  document.querySelectorAll('[data-cart-form]').forEach(bind);
  document.addEventListener('htmx:afterSwap', event => event.detail.target.querySelectorAll('[data-cart-form]').forEach(bind));
  document.querySelector('[data-checkout-error]')?.focus();
})();
