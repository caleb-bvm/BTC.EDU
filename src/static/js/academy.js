(() => {
  let catalogFocus = null;
  let catalogRefinementsOpen = false;
  const scopeTopicChoices = (form) => {
    const category = form.querySelector('select[name="categoria"]');
    const topic = form.querySelector('select[name="tema"]');
    if (!category || !topic) return;
    topic.querySelectorAll('option[data-category]').forEach((option) => {
      const available = !category.value || option.dataset.category === category.value;
      option.hidden = !available;
      option.disabled = !available;
    });
    topic.querySelectorAll('optgroup').forEach((group) => {
      group.hidden = [...group.querySelectorAll('option')].every((option) => option.hidden);
      group.disabled = group.hidden;
    });
  };
  document.querySelectorAll('.catalog-filterbar').forEach(scopeTopicChoices);
  document.addEventListener('change', (event) => {
    const form = event.target.closest('.academy-filters');
    if (!form) return;
    const category = form.querySelector('[name="categoria"]');
    const topic = form.querySelector('[name="tema"]');
    if (!category || !topic) return;
    if (event.target === category && category.tagName === 'SELECT') topic.value = '';
    if (event.target === topic && topic.value && category.tagName === 'SELECT') category.value = topic.selectedOptions[0]?.dataset.category || '';
    scopeTopicChoices(form);
  });
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
    if (event.detail.elt?.closest('#catalog')) {
      catalogFocus = document.activeElement?.id || 'catalog-query';
      catalogRefinementsOpen = Boolean(event.detail.elt.closest('#catalog').querySelector('#catalog-refinements')?.open);
    }
  });
  document.addEventListener('htmx:afterSettle', (event) => {
    if (event.detail.target?.id !== 'catalog') return;
    updateCatalogTabs();
    const catalog = document.getElementById('catalog');
    const refinements = catalog?.querySelector('#catalog-refinements');
    if (refinements) refinements.open = catalogRefinementsOpen;
    catalog?.querySelectorAll('.catalog-filterbar').forEach(scopeTopicChoices);
    if (document.activeElement === document.body && catalogFocus) {
      const target = document.getElementById(catalogFocus);
      (target?.getClientRects().length ? target : document.getElementById('catalog-query'))?.focus({preventScroll:true});
    }
    catalogFocus = null;
    catalogRefinementsOpen = false;
  });
  document.addEventListener('htmx:pushedIntoHistory', updateCatalogTabs);
  window.addEventListener('popstate', updateCatalogTabs);
  const toggle = document.querySelector('.nav-toggle');
  const backdrop = document.querySelector('.nav-backdrop');
  const navigation = document.querySelector('#academy-navigation');
  if (toggle && backdrop && navigation) {
    document.documentElement.classList.add('js-ready');
    const desktop = window.matchMedia('(min-width: 901px)');
    const closeButton = navigation.querySelector('.nav-close');
    let inertElements = [];
    const focusableLinks = () => [...navigation.querySelectorAll('a[href],button:not([disabled]),[tabindex="0"]')]
      .filter(element => element.getClientRects().length && !element.closest('[inert]'));
    const restoreBackground = () => {
      inertElements.forEach(([element, previous]) => { element.inert = previous; });
      inertElements = [];
    };
    const lockBackground = () => {
      // Inert siblings at each level, keeping the dialog itself interactive.
      for (let branch = navigation; branch.parentElement && branch !== document.body; branch = branch.parentElement) {
        [...branch.parentElement.children].forEach(element => {
          if (element === branch || element === backdrop) return;
          inertElements.push([element, element.inert]);
          element.inert = true;
        });
      }
    };
    const header = document.querySelector('.academy-header');
    if (header) {
      const updateMenuOffset = () => document.documentElement.style.setProperty('--academy-nav-offset', `${header.getBoundingClientRect().height}px`);
      updateMenuOffset();
      if (window.ResizeObserver) new ResizeObserver(updateMenuOffset).observe(header);
      else window.addEventListener('resize', updateMenuOffset);
    }
    const setOpen = (open, restoreFocus = false) => {
      open = open && (!desktop.matches || document.body.classList.contains('reader-focused'));
      restoreBackground();
      document.body.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Cerrar menú principal' : 'Abrir menú principal');
      backdrop.hidden = !open;
      if (open) {
        navigation.setAttribute('role', 'dialog');
        navigation.setAttribute('aria-modal', 'true');
        lockBackground();
        (navigation.querySelector('[aria-current="page"]') || closeButton || navigation).focus();
      } else {
        navigation.removeAttribute('role');
        navigation.removeAttribute('aria-modal');
        if (restoreFocus) toggle.focus({preventScroll: true});
      }
    };
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    backdrop.addEventListener('click', () => setOpen(false, true));
    closeButton?.addEventListener('click', () => setOpen(false, true));
    navigation.addEventListener('click', (event) => {
      if (!event.target.closest('a') || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      // A form's unsaved-changes guard may still cancel this navigation.
      queueMicrotask(() => { if (!event.defaultPrevented) setOpen(false, true); });
    });
    document.addEventListener('keydown', (event) => {
      if (!document.body.classList.contains('nav-open')) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        event.stopPropagation();
        setOpen(false, true);
      } else if (event.key === 'Tab') {
        const links = focusableLinks();
        const first = links[0] || navigation;
        const last = links.at(-1) || navigation;
        if (event.shiftKey && (document.activeElement === first || document.activeElement === navigation)) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }, true);
    document.addEventListener('focusin', (event) => {
      if (document.body.classList.contains('nav-open') && !navigation.contains(event.target)) (focusableLinks()[0] || navigation).focus();
    });
    desktop.addEventListener('change', () => setOpen(false));
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
