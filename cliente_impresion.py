# cliente_impresion.py - Comandero
import requests
import time
import os
import socket
import usb.core
from datetime import datetime

# ==================== SOLO ESTO CONFIGURA EL USUARIO ====================
API_URL       = "https://app-resto-production.up.railway.app"
ARCHIVO_KEY   = "api_key.txt"
ARCHIVO_IMPRESOS = "pedidos_impresos.txt"
CHECK_INTERVAL = 10
# =========================================================================


def pedir_api_key():
    """Pide la API Key al usuario y la guarda para la próxima vez"""
    if os.path.exists(ARCHIVO_KEY):
        with open(ARCHIVO_KEY) as f:
            key = f.read().strip()
        if key:
            print(f"✅ API Key cargada desde archivo")
            return key
    print("=" * 45)
    print("  Bienvenido a Comandero - Cliente de impresión")
    print("=" * 45)
    print("Encontrá tu API Key en: Configuración → Información del Plan")
    print()
    key = input("Ingresá tu API Key: ").strip()
    with open(ARCHIVO_KEY, "w") as f:
        f.write(key)
    return key


def obtener_config(api_key):
    """Descarga la configuración de impresora desde la app"""
    try:
        r = requests.get(f"{API_URL}/api/public/config/{api_key}", timeout=10)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            print("❌ API Key incorrecta. Borrá el archivo api_key.txt y volvé a intentar.")
            return None
        else:
            print(f"Error obteniendo config: {r.status_code}")
            return None
    except Exception as e:
        print(f"Error conectando al servidor: {e}")
        return None


def detectar_impresoras_usb():
    """Detecta impresoras USB conectadas y deja elegir al usuario"""
    try:
        import usb.core
        dispositivos = list(usb.core.find(find_all=True))
        impresoras = []
        # Clase USB 7 = impresoras
        for d in dispositivos:
            try:
                if d.bDeviceClass == 7 or any(
                    cfg.bNumInterfaces > 0 and any(
                        intf.bInterfaceClass == 7
                        for intf in cfg
                    )
                    for cfg in d
                ):
                    impresoras.append(d)
            except:
                pass

        if not impresoras:
            print("⚠️  No se encontraron impresoras USB.")
            return None, None

        print("\nImpresoras USB detectadas:")
        for i, d in enumerate(impresoras):
            try:
                nombre = usb.util.get_string(d, d.iProduct) if d.iProduct else "Desconocido"
            except:
                nombre = "Desconocido"
            print(f"  [{i+1}] {nombre} — Vendor: 0x{d.idVendor:04x} Product: 0x{d.idProduct:04x}")

        eleccion = input("\nElegí el número de tu impresora: ").strip()
        idx = int(eleccion) - 1
        d = impresoras[idx]
        return d.idVendor, d.idProduct

    except ImportError:
        print("⚠️  Librería 'pyusb' no instalada. Instalala con: pip install pyusb")
        return None, None
    except Exception as e:
        print(f"Error detectando USB: {e}")
        return None, None


def cargar_impresos():
    if os.path.exists(ARCHIVO_IMPRESOS):
        with open(ARCHIVO_IMPRESOS) as f:
            return set(int(x) for x in f.read().split() if x)
    return set()


def guardar_impreso(pedido_id):
    with open(ARCHIVO_IMPRESOS, "a") as f:
        f.write(f"{pedido_id}\n")


def construir_comanda(pedido):
    lineas = []
    lineas.append("================================\n")
    lineas.append("          COMANDA\n")
    lineas.append("================================\n")
    if pedido.get("tipo_consumo") == "Local":
        lineas.append(f"MESA: {pedido.get('mesa', 'N/A')}\n")
    else:
        lineas.append("PARA LLEVAR\n")
        lineas.append(f"Cliente: {pedido.get('nombre_cliente', 'N/A')}\n")
    try:
        fecha = datetime.fromisoformat(pedido.get("fecha", "").replace("Z", "+00:00"))
        lineas.append(f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}\n")
    except:
        lineas.append(f"Fecha: {pedido.get('fecha', '')}\n")
    lineas.append(f"Pedido #{pedido.get('id')}\n")
    lineas.append("--------------------------------\n")
    total = 0
    for item in pedido.get("items", []):
        precio = item.get("precio", 0)
        total += precio
        nombre = item.get("nombre", "Producto")[:20]
        lineas.append(f"{nombre:<20}${precio:>8.0f}\n")
    lineas.append("--------------------------------\n")
    lineas.append(f"TOTAL: ${total:.0f}\n")
    lineas.append(f"Pago: {pedido.get('metodo_pago', 'N/A')}\n")
    lineas.append("================================\n")
    lineas.append("       Buen provecho!\n\n\n")
    return lineas


def imprimir_usb(lineas, vendor_id, product_id):
    try:
        from escpos.printer import Usb
        printer = Usb(vendor_id, product_id)
        for linea in lineas:
            printer.text(linea)
        printer.cut()
        printer.close()
        return True
    except Exception as e:
        print(f"Error impresora USB: {e}")
        return False


def imprimir_red(lineas, ip, puerto):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, int(puerto)))
            texto = "".join(lineas).encode("cp858", errors="replace")
            s.sendall(texto)
            s.sendall(b'\x1d\x56\x00')  # cortar papel ESC/POS
        return True
    except Exception as e:
        print(f"Error impresora red: {e}")
        return False


def obtener_pedidos(api_key):
    try:
        r = requests.get(f"{API_URL}/api/public/pedidos/{api_key}", timeout=10)
        if r.status_code == 200:
            return r.json().get("pedidos", [])
        return []
    except Exception as e:
        print(f"Error consultando pedidos: {e}")
        return []


def main():
    api_key = pedir_api_key()

    print("\nConectando con el servidor...")
    config = obtener_config(api_key)
    if not config:
        return

    if not config.get("habilitada"):
        print("⚠️  La impresión está deshabilitada en la configuración del restaurante.")
        print("   Activala desde Configuración → Habilitar impresión de comandas")
        return

    tipo = config.get("tipo", "USB")
    vendor_id = product_id = ip = puerto = None

    if tipo == "USB":
        print("\nDetectando impresoras USB...")
        vendor_id, product_id = detectar_impresoras_usb()
        if not vendor_id:
            print("No se pudo detectar impresora USB. Saliendo.")
            return
    else:
        ip     = config.get("ip")
        puerto = config.get("puerto", 9100)
        print(f"✅ Impresora de red: {ip}:{puerto}")

    pedidos_impresos = cargar_impresos()
    print(f"\n✅ Todo listo. Esperando pedidos cada {CHECK_INTERVAL} segundos...")
    print("   (Ctrl+C para detener)\n")

    while True:
        try:
            pedidos = obtener_pedidos(api_key)
            for pedido in pedidos:
                pedido_id = pedido.get("id")
                if pedido_id not in pedidos_impresos:
                    print(f"🖨️  Nuevo pedido #{pedido_id} — imprimiendo...")
                    lineas = construir_comanda(pedido)
                    if tipo == "USB":
                        ok = imprimir_usb(lineas, vendor_id, product_id)
                    else:
                        ok = imprimir_red(lineas, ip, puerto)
                    if ok:
                        pedidos_impresos.add(pedido_id)
                        guardar_impreso(pedido_id)
                        print(f"✅ Pedido #{pedido_id} impreso")
                    else:
                        print(f"❌ Error, se reintentará en el próximo ciclo")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nCliente detenido.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()