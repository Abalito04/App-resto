// === Registro del service worker ===
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").then(reg => {
    console.log("Service Worker registrado:", reg);
    initPush(reg);
  });
}

// === Función para inicializar Push ===
async function initPush(registration) {
  const permission = await Notification.requestPermission();
  if (permission !== "granted") {
    console.log("Permiso de notificación denegado");
    return;
  }

  // Suscribir al usuario
  const PUBLIC_VAPID_KEY = "TU_CLAVE_PUBLICA";
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(PUBLIC_VAPID_KEY)
  });

  // Enviar suscripción al servidor
  await fetch("/subscribe", {
    method: "POST",
    body: JSON.stringify(subscription),
    headers: { "Content-Type": "application/json" }
  });

  console.log("Usuario suscripto a notificaciones!");
}

// Helper para convertir la clave pública
function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));
}
