(() => {
  let catalogFocus = null;
  const updateCatalogTabs = () => {
    const parameters = new URLSearchParams(window.location.search);
    parameters.delete('pagina');
    parameters.delete('curso');
    document.querySelectorAll('[data-catalog-view]').forEach((link) => {
      const query = parameters.toString();
      link.href = link.dataset.catalogView + (query ? '?' + query : '');
    });
  };
  document.addEventListener('htmx:beforeRequest', (event) => {
    if (event.detail.elt?.closest('#catalog')) catalogFocus = document.activeElement?.id || 'catalog-query';
  });
  document.addEventListener('htmx:afterSettle', (event) => {
    if (event.detail.target?.id !== 'catalog') return;
    updateCatalogTabs();
    if (document.activeElement === document.body && catalogFocus) {
      document.getElementById(catalogFocus)?.focus({preventScroll:true});
    }
    catalogFocus = null;
  });
  document.addEventListener('htmx:pushedIntoHistory', updateCatalogTabs);
  window.addEventListener('popstate', updateCatalogTabs);
  const toggle = document.querySelector('.nav-toggle');
  const backdrop = document.querySelector('.nav-backdrop');
  const navigation = document.querySelector('#academy-navigation');
  if (toggle && backdrop && navigation) {
    document.documentElement.classList.add('js-ready');
    const setOpen = (open, restoreFocus = false) => {
      document.body.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      backdrop.hidden = !open;
      if (open) navigation.querySelector('a')?.focus();
      else if (restoreFocus) toggle.focus();
    };
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    backdrop.addEventListener('click', () => setOpen(false, true));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && document.body.classList.contains('nav-open')) setOpen(false, true);
    });
    document.addEventListener('focusin', (event) => {
      if (document.body.classList.contains('nav-open') && !navigation.contains(event.target) && event.target !== toggle) setOpen(false);
    });
    window.matchMedia('(min-width: 901px)').addEventListener('change', () => setOpen(false));
  }
  document.addEventListener('htmx:responseError', (event) => {
    if (event.detail.target?.id !== 'catalog') return;
    let error = document.getElementById('catalog-error');
    if (!error) {
      error = document.createElement('p');
      error.id = 'catalog-error';
      error.className = 'form-error';
      error.setAttribute('role', 'alert');
      event.detail.target.prepend(error);
    }
    error.textContent = 'No pudimos actualizar el catálogo. Tus filtros siguen aquí; vuelve a intentarlo.';
  });
  document.addEventListener('htmx:sendError', (event) => {
    const catalog = document.getElementById('catalog');
    if (!catalog || !event.detail.elt?.closest('#catalog')) return;
    let error = document.getElementById('catalog-error');
    if (!error) {
      error = document.createElement('p');
      error.id = 'catalog-error';
      error.className = 'form-error';
      error.setAttribute('role', 'alert');
      catalog.prepend(error);
    }
    error.textContent = 'Se perdió la conexión. Conservamos tus filtros; vuelve a buscar cuando recuperes conexión.';
  });
})();
const paymentStatus = document.querySelector('[data-invoice-status]');
if (paymentStatus) {
  const checkPayment = async () => {
    if (document.hidden) {
      window.setTimeout(checkPayment, 5000);
      return;
    }
    try {
      const response = await fetch(paymentStatus.dataset.invoiceStatus, {cache: 'no-store', headers: {'Accept': 'application/json'}});
      if (!response.ok || response.redirected) throw new Error('Payment check failed');
      const result = await response.json();
      if (result.status !== 'pending' || result.incident) {
        window.location.reload();
        return;
      }
    } catch {
      paymentStatus.textContent = 'No pudimos comprobar el pago. Usa Actualizar estado para volver a intentarlo.';
      paymentStatus.hidden = false;
      return;
    }
    window.setTimeout(checkPayment, 5000);
  };
  window.setTimeout(checkPayment, 5000);
}
document.addEventListener('error', (event) => {
  if (event.target instanceof HTMLVideoElement) {
    const message = event.target.closest('.media-panel')?.querySelector('.media-error');
    if (message) message.hidden = false;
  }
}, true);
