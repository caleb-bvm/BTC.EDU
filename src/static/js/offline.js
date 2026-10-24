"use strict";

(() => {
  const SAVED = "btc-edu-saved";
  const INDEX = "/__btc-edu-saved-index__";
  const supported = "serviceWorker" in navigator && "caches" in window;
  if (!supported) return;

  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });

  const account = document.querySelector('meta[name="btc-account-id"]')?.content || "";

  const readIndex = async () => {
    const cache = await caches.open(SAVED);
    const response = await cache.match(INDEX);
    const index = response ? await response.json().catch(() => null) : null;
    return {cache, index: index && Array.isArray(index.pages) ? index : {account, pages: []}};
  };

  const writeIndex = (cache, index) => cache.put(INDEX, new Response(JSON.stringify(index), {headers: {"Content-Type": "application/json"}}));

  // Saved lessons belong to one account: another account or signing out removes them.
  const guard = async () => {
    const {index} = await readIndex();
    if (index.pages.length && index.account !== account && !document.body.classList.contains("offline-page")) {
      await caches.delete(SAVED);
    }
  };

  const setButton = (button, saved) => {
    button.setAttribute("aria-pressed", saved ? "true" : "false");
    button.textContent = saved ? "Disponible sin conexión ✓" : "Guardar sin conexión";
  };

  const initButtons = async () => {
    const buttons = document.querySelectorAll("[data-offline-save]");
    if (!buttons.length || !account) return;
    const path = window.location.pathname;
    buttons.forEach(async (button) => {
      const {index} = await readIndex();
      setButton(button, index.pages.some((page) => page.url === path));
      button.hidden = false;
      button.addEventListener("click", async () => {
        const state = await readIndex();
        const saved = state.index.pages.some((page) => page.url === path);
        button.disabled = true;
        try {
          if (saved) {
            await state.cache.delete(path);
            state.index.pages = state.index.pages.filter((page) => page.url !== path);
          } else {
            const response = await fetch(path, {credentials: "same-origin", cache: "no-store"});
            if (!response.ok || response.redirected) throw new Error("not saved");
            await state.cache.put(path, response);
            state.index.pages = state.index.pages.filter((page) => page.url !== path);
            state.index.pages.unshift({url: path, title: button.dataset.offlineTitle, course: button.dataset.offlineCourse, saved_at: new Date().toISOString()});
          }
          state.index.account = account;
          await writeIndex(state.cache, state.index);
          setButton(button, !saved);
        } catch {
          button.textContent = "No se pudo guardar. Inténtalo con conexión.";
        } finally {
          button.disabled = false;
        }
      });
    });
  };

  const initOfflineList = async () => {
    const list = document.querySelector("[data-offline-list]");
    if (!list) return;
    const {index} = await readIndex();
    const empty = document.querySelector("[data-offline-empty]");
    if (!index.pages.length) {
      if (empty) empty.hidden = false;
      return;
    }
    index.pages.forEach((page) => {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = page.url;
      link.textContent = page.title || page.url;
      const course = document.createElement("small");
      course.textContent = page.course || "";
      item.append(link, course);
      list.append(item);
    });
    list.hidden = false;
  };

  guard().then(initButtons).then(initOfflineList).catch(() => {});
})();
