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

document.querySelectorAll("[data-copy-payment]").forEach((button) => {
  button.addEventListener("click", async () => {
    const input = document.getElementById(button.dataset.copyPayment);
    const status = button.parentElement.querySelector("[data-copy-status]");
    if (!input || !status) return;
    try {
      await navigator.clipboard.writeText(input.value);
      status.textContent = "Factura copiada.";
    } catch {
      input.focus();
      input.select();
      status.textContent = "Seleccionamos la factura. Usa la opción de copiar de tu dispositivo.";
    }
    status.hidden = false;
  });
});

document.querySelectorAll("[data-tip-preset]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById("id_amount");
    if (!input) return;
    input.value = button.dataset.tipPreset;
    input.focus();
  });
});
