// app.js

// Registrar el Service Worker
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/sw.js")
      .then(reg => {
        console.log("✅ Service Worker registrado con éxito:", reg.scope);
      })
      .catch(err => {
        console.error("❌ Error al registrar el Service Worker:", err);
      });
  });
}

// Solicitar permiso para notificaciones (solo si el navegador lo soporta)
function solicitarPermisoNotificaciones() {
  if ("Notification" in window && Notification.permission !== "granted") {
    Notification.requestPermission().then(permission => {
      console.log("Permiso de notificaciones:", permission);
    });
  }
}

// Ejecutamos la solicitud al cargar
solicitarPermisoNotificaciones();
