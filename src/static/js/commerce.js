"use strict";

const paymentForms = document.querySelectorAll("[data-payment-form]");
paymentForms.forEach((form) => {
  // Buttons outside the form (the phone total bar) submit it through the form attribute.
  const buttons = [...form.querySelectorAll('button[type="submit"]'), ...(form.id ? document.querySelectorAll(`button[type="submit"][form="${form.id}"]`) : [])];
  if (!buttons.length) return;
  const labels = buttons.map((button) => button.textContent);
  form.addEventListener("submit", () => {
    form.setAttribute("aria-busy", "true");
    buttons.forEach((button) => {
      button.disabled = true;
      button.textContent = form.dataset.pendingLabel;
    });
  });
  window.addEventListener("pageshow", () => {
    buttons.forEach((button, index) => {
      button.disabled = false;
      button.textContent = labels[index];
    });
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
