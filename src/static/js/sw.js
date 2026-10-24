"use strict";

// Keep in sync with core/pwa.py; bumping VERSION drops old shell and static caches.
const VERSION = "btc-edu-v1";
const SHELL = `${VERSION}-shell`;
const STATIC = `${VERSION}-static`;
const SAVED = "btc-edu-saved";
const OFFLINE_URL = "/sin-conexion/";

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(SHELL).then((cache) => cache.add(OFFLINE_URL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((key) => key.startsWith("btc-edu-v") && !key.startsWith(VERSION)).map((key) => caches.delete(key))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(caches.open(STATIC).then(async (cache) => {
      const cached = await cache.match(request);
      const network = fetch(request).then((response) => {
        if (response.ok) cache.put(request, response.clone());
        return response;
      }).catch(() => cached);
      return cached || network;
    }));
    return;
  }
  if (request.mode === "navigate") {
    // Pages always come from the network; only lessons the student saved work offline.
    event.respondWith(fetch(request).catch(async () => {
      const saved = await caches.open(SAVED);
      return (await saved.match(url.pathname)) || (await caches.match(OFFLINE_URL)) || Response.error();
    }));
  }
});
