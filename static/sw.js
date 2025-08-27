// static/sw.js - Service Worker optimizado
const CACHE_NAME = "resto-cache-v2";
const urlsToCache = [
  "/",
  "/static/style.css",
  "/static/icon-192.png",
  "/static/icon-512.png"
];
const MAX_CACHE_ITEMS = 50; // Limitar tamaño del caché

// Limpiar caché viejo
async function cleanCache(cacheName, maxItems) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  if (keys.length > maxItems) {
    await cache.delete(keys[0]);
    cleanCache(cacheName, maxItems);
  }
}

// Instalación
self.addEventListener("install", (event) => {
  console.log("📦 Instalando Service Worker...");
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log("Archivos cacheados");
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.log("Error cacheando:", error);
      })
  );
  self.skipWaiting();
});

// Activación
self.addEventListener("activate", (event) => {
  console.log("⚡ Service Worker activado");
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log("🗑️ Eliminando cache viejo:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch con fallback
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) return response;

      return fetch(event.request)
        .then((networkResponse) => {
          if (!networkResponse || networkResponse.status !== 200) {
            return networkResponse;
          }

          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
            cleanCache(CACHE_NAME, MAX_CACHE_ITEMS);
          });

          return networkResponse;
        })
        .catch(() => {
          // Fallbacks
          if (event.request.destination === "document") {
            return caches.match("/");
          }
          if (event.request.destination === "image") {
            return caches.match("/static/icon-192.png");
          }
        });
    })
  );
});

// Notificaciones push
self.addEventListener("push", (event) => {
  console.log("📩 Notificación recibida:", event.data?.text());

  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = { title: "Restaurante App", body: "Nuevo pedido recibido" };
  }

  const options = {
    body: data.body || "Nuevo pedido recibido",
    icon: "/static/icon-192.png",
    badge: "/static/icon-192.png",
    tag: "nuevo-pedido"
  };

  event.waitUntil(
    self.registration.showNotification(data.title || "Restaurante App", options)
  );
});

// Click en notificación
self.addEventListener("notificationclick", (event) => {
  console.log("🖱️ Click en notificación");
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === "/" && "focus" in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow("/");
      }
    })
  );
});
