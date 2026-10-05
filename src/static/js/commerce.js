"use strict";

const paymentForms = document.querySelectorAll("[data-payment-form]");
paymentForms.forEach((form) => {
  const button = form.querySelector('button[type="submit"]');
  if (!button) return;
  const label = button.textContent;
  form.addEventListener("submit", () => {
    button.disabled = true;
    form.setAttribute("aria-busy", "true");
    button.textContent = form.dataset.pendingLabel;
  });
  window.addEventListener("pageshow", () => {
    button.disabled = false;
    button.textContent = label;
    form.removeAttribute("aria-busy");
  });
});
