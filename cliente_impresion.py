# cliente_impresion.py
import requests
import time
from datetime import datetime
from escpos.printer import Usb
import json

# Configuración
API_URL = "https://app-resto-production.up.railway.app"
PRINTER_VENDOR_ID = 0x04b8
PRINTER_PRODUCT_ID = 0x0202
CHECK_INTERVAL = 10  # segundos entre consultas

# IDs de pedidos ya procesados
pedidos_impresos = set()

def conectar_impresora():
    """Intenta conectar con la impresora USB"""
    try:
        printer = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)
        return printer
    except Exception as e:
        print(f"Error conectando impresora: {e}")
        return None

def imprimir_comanda_local(pedido_data, printer):
    """Imprime la comanda usando la impresora local"""
    try:
        # Header
        printer.set(align='center', text_type='B', width=2, height=2)
        printer.text("COMANDA\n")
        printer.set()
        
        # Info del pedido
        printer.text("=" * 32 + "\n")
        
        if pedido_data.get('tipo_consumo') == "Local":
            printer.text(f"MESA: {pedido_data.get('mesa', 'N/A')}\n")
        else:
            printer.text("PARA LLEVAR\n")
            printer.text(f"Cliente: {pedido_data.get('nombre_cliente', 'N/A')}\n")
        
        # Fecha (convertir de ISO)
        fecha_str = pedido_data.get('fecha', '')
        try:
            fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            printer.text(f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}\n")
        except:
            printer.text(f"Fecha: {fecha_str}\n")
        
        printer.text(f"Pedido #{pedido_data.get('id')}\n")
        printer.text("-" * 32 + "\n")
        
        # Items
        total = 0
        for item in pedido_data.get('items', []):
            precio = item.get('precio', 0)
            total += precio
            nombre = item.get('nombre', 'Producto')[:20]
            linea = f"{nombre:<20}${precio:>8.0f}\n"
            printer.text(linea)
        
        printer.text("-" * 32 + "\n")
        
        # Total
        printer.set(text_type='B')
        printer.text(f"TOTAL: ${total:.0f}\n")
        printer.set()
        
        # Método de pago
        printer.text(f"Pago: {pedido_data.get('metodo_pago', 'N/A')}\n")
        
        printer.text("=" * 32 + "\n")
        printer.set(align='center')
        printer.text("Buen provecho!\n\n\n")
        
        printer.cut()
        printer.close()
        
        print(f"Comanda impresa para pedido #{pedido_data.get('id')}")
        return True
        
    except Exception as e:
        print(f"Error imprimiendo: {e}")
        return False

def obtener_pedidos_pendientes():
    """Consulta la API por pedidos pendientes"""
    try:
        response = requests.get(f"{API_URL}/api/pedidos/activos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('pedidos', [])
        else:
            print(f"Error API: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error consultando API: {e}")
        return []

def main():
    """Loop principal del cliente"""
    print("Cliente de impresión iniciado")
    print(f"API: {API_URL}")
    print(f"Consultando cada {CHECK_INTERVAL} segundos...")
    
    # Verificar impresora al inicio
    printer_test = conectar_impresora()
    if printer_test:
        print("Impresora conectada correctamente")
        printer_test.close()
    else:
        print("ADVERTENCIA: No se pudo conectar con la impresora")
        print("Revisa que esté encendida y conectada por USB")
        return
    
    while True:
        try:
            # Obtener pedidos pendientes
            pedidos = obtener_pedidos_pendientes()
            
            # Procesar pedidos nuevos
            for pedido in pedidos:
                pedido_id = pedido.get('id')
                
                if pedido_id not in pedidos_impresos:
                    print(f"Nuevo pedido detectado: #{pedido_id}")
                    
                    # Conectar impresora para este pedido
                    printer = conectar_impresora()
                    if printer:
                        if imprimir_comanda_local(pedido, printer):
                            pedidos_impresos.add(pedido_id)
                            print(f"Pedido #{pedido_id} marcado como impreso")
                        else:
                            print(f"Error imprimiendo pedido #{pedido_id}")
                    else:
                        print("No se pudo conectar con la impresora")
            
            # Esperar antes de la próxima consulta
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nCliente detenido por el usuario")
            break
        except Exception as e:
            print(f"Error en loop principal: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Configuración de impresora
    print("Configuración actual:")
    print(f"Vendor ID: 0x{PRINTER_VENDOR_ID:04x}")
    print(f"Product ID: 0x{PRINTER_PRODUCT_ID:04x}")
    print("¿Es correcta? (Enter para continuar, Ctrl+C para salir)")
    input()
    
    main()