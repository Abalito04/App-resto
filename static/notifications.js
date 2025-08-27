// notifications.js

// Función para mostrar notificación local
function mostrarNotificacion(titulo, opciones) {
  if ("Notification" in window && Notification.permission === "granted") {
    navigator.serviceWorker.ready.then(reg => {
      reg.showNotification(titulo, opciones);
    });
  }
}

// Ejemplo: notificación cuando entra un pedido nuevo
function notificarNuevoPedido(pedido) {
  mostrarNotificacion("🛎️ Nuevo Pedido", {
    body: `Mesa ${pedido.mesa} - ${pedido.items.join(", ")}`,
    icon: "/static/icon-192.png",
    badge: "/static/icon-192.png",
    vibrate: [200, 100, 200]
  });
}

// Exportar para usar en otras partes
window.notificarNuevoPedido = notificarNuevoPedido;
