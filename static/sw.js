// static/sw.js - Service Worker simplificado
const CACHE_NAME = "resto-cache-v1";
const urlsToCache = [
  "/",
  "/static/style.css",
  "/static/icon-192.png",
  "/static/icon-512.png"
];

// Instalación
self.addEventListener("install", (event) => {
  console.log("Service Worker instalando...");
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
  console.log("Service Worker activado");
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log("Eliminando cache viejo:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        
        return fetch(event.request).then((response) => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
      .catch(() => {
        // Fallback para páginas offline
        if (event.request.destination === 'document') {
          return caches.match('/');
        }
      })
  );
});

// Notificaciones simples
self.addEventListener("push", function(event) {
  console.log("Notificación recibida");
  
  const options = {
    title: "Restaurante App",
    body: "Nuevo pedido recibido",
    icon: "/static/icon-192.png",
    badge: "/static/icon-192.png",
    tag: "nuevo-pedido"
  };

  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// Click en notificación
self.addEventListener("notificationclick", function(event) {
  console.log("Click en notificación");
  event.notification.close();

  event.waitUntil(
    clients.matchAll().then((clientList) => {
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