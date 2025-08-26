// static/notifications.js - Manejo de notificaciones
class NotificationManager {
    constructor() {
        this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
        this.registration = null;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.log("❌ Notificaciones no soportadas");
            return;
        }

        try {
            // Registrar Service Worker
            this.registration = await navigator.serviceWorker.register('/static/sw.js');
            console.log("✅ Service Worker registrado");

            // Solicitar permisos de notificación
            await this.requestPermission();
            
            // Configurar suscripción push si hay permisos
            if (Notification.permission === 'granted') {
                await this.setupPushSubscription();
            }

        } catch (error) {
            console.error("❌ Error inicializando notificaciones:", error);
        }
    }

    async requestPermission() {
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log("🔔 Permiso de notificación:", permission);
            return permission;
        }
        return Notification.permission;
    }

    async setupPushSubscription() {
        try {
            // En una implementación real, necesitarías una clave VAPID
            // const subscription = await this.registration.pushManager.subscribe({
            //     userVisibleOnly: true,
            //     applicationServerKey: 'TU_CLAVE_VAPID_PUBLICA'
            // });

            // Enviar suscripción al servidor
            // await fetch('/api/subscribe', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(subscription)
            // });

            console.log("📱 Suscripción push configurada");
        } catch (error) {
            console.error("❌ Error configurando push:", error);
        }
    }

    // Mostrar notificación local
    showLocalNotification(title, options = {}) {
        if (Notification.permission === 'granted') {
            const notification = new Notification(title, {
                icon: '/static/icon-192.png',
                badge: '/static/icon-192.png',
                ...options
            });

            notification.onclick = function() {
                window.focus();
                this.close();
            };

            return notification;
        }
    }

    // Monitorear pedidos nuevos
    startOrderMonitoring() {
        let lastOrderCount = 0;

        setInterval(async () => {
            try {
                const response = await fetch('/api/pedidos/activos');
                const data = await response.json();

                if (data.count > lastOrderCount && lastOrderCount > 0) {
                    this.showLocalNotification('¡Nuevo pedido!', {
                        body: `Hay ${data.count} pedidos activos`,
                        tag: 'nuevo-pedido',
                        vibrate: [200, 100, 200]
                    });
                }

                lastOrderCount = data.count;
            } catch (error) {
                console.error("Error monitoreando pedidos:", error);
            }
        }, 10000); // Cada 10 segundos
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    const notificationManager = new NotificationManager();
    
    // Solo monitorear en la página de cocina
    if (window.location.pathname === '/cocina') {
        notificationManager.startOrderMonitoring();
    }

    // Botón para solicitar permisos manualmente
    const enableNotificationsBtn = document.getElementById('enable-notifications');
    if (enableNotificationsBtn) {
        enableNotificationsBtn.addEventListener('click', async () => {
            const permission = await notificationManager.requestPermission();
            if (permission === 'granted') {
                enableNotificationsBtn.style.display = 'none';
                notificationManager.startOrderMonitoring();
            }
        });
    }
});