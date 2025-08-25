const CACHE_NAME = "resto-cache-v1";
const urlsToCache = [
  "/",
  "/static/style.css",
  "/static/icon-192.png",
  "/static/icon-512.png"
];

// Instalación y cache inicial
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// Activación
self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

// Fetch: servir archivos cacheados o de la red
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
