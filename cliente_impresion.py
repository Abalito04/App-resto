# cliente_impresion.py
import requests
import time
import os
import socket
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
API_URL = "https://app-resto-production.up.railway.app"
API_KEY = "tu_api_key_aqui"  # Copiá la API Key desde Configuración

MODO_IMPRESORA = "USB"  # "USB" o "NETWORK"

# Solo para USB:
PRINTER_VENDOR_ID  = 0x04b8
PRINTER_PRODUCT_ID = 0x0202

# Solo para red:
PRINTER_IP   = "192.168.1.100"
PRINTER_PORT = 9100

CHECK_INTERVAL  = 10  # segundos entre consultas
ARCHIVO_IMPRESOS = "pedidos_impresos.txt"
# =======================================================


def cargar_impresos():
    if os.path.exists(ARCHIVO_IMPRESOS):
        with open(ARCHIVO_IMPRESOS) as f:
            return set(int(x) for x in f.read().split() if x)
    return set()


def guardar_impreso(pedido_id):
    with open(ARCHIVO_IMPRESOS, "a") as f:
        f.write(f"{pedido_id}\n")


def imprimir_usb(lineas):
    try:
        from escpos.printer import Usb
        printer = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)
        for linea in lineas:
            printer.text(linea)
        printer.cut()
        printer.close()
        return True
    except Exception as e:
        print(f"Error impresora USB: {e}")
        return False


def imprimir_red(lineas):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((PRINTER_IP, PRINTER_PORT))
            texto = "".join(lineas).encode("cp858", errors="replace")
            s.sendall(texto)
            # Comando ESC/POS para cortar papel
            s.sendall(b'\x1d\x56\x00')
        return True
    except Exception as e:
        print(f"Error impresora red: {e}")
        return False


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

    fecha_str = pedido.get("fecha", "")
    try:
        fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        lineas.append(f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}\n")
    except:
        lineas.append(f"Fecha: {fecha_str}\n")

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
    lineas.append("       Buen provecho!\n")
    lineas.append("\n\n\n")
    return lineas


def imprimir_comanda(pedido):
    lineas = construir_comanda(pedido)
    if MODO_IMPRESORA == "USB":
        return imprimir_usb(lineas)
    else:
        return imprimir_red(lineas)


def obtener_pedidos_pendientes():
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(
            f"{API_URL}/api/pedidos/activos",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("pedidos", [])
        elif response.status_code == 401:
            print("❌ API Key incorrecta — verificá la configuración")
            return []
        else:
            print(f"Error API: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error consultando API: {e}")
        return []


def main():
    print("=" * 40)
    print("  Cliente de impresión - Comandero")
    print("=" * 40)
    print(f"Modo: {MODO_IMPRESORA}")
    print(f"API: {API_URL}")
    print(f"Consultando cada {CHECK_INTERVAL} segundos...")
    print()

    pedidos_impresos = cargar_impresos()
    print(f"Pedidos ya impresos cargados: {len(pedidos_impresos)}")

    while True:
        try:
            pedidos = obtener_pedidos_pendientes()

            for pedido in pedidos:
                pedido_id = pedido.get("id")
                if pedido_id not in pedidos_impresos:
                    print(f"Nuevo pedido detectado: #{pedido_id}")
                    if imprimir_comanda(pedido):
                        pedidos_impresos.add(pedido_id)
                        guardar_impreso(pedido_id)
                        print(f"✅ Pedido #{pedido_id} impreso correctamente")
                    else:
                        print(f"❌ Error imprimiendo pedido #{pedido_id}, se reintentará")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\nCliente detenido.")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()