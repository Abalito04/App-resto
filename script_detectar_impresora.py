# script_detectar_impresora.py
import usb.core

print("Dispositivos USB detectados:")
for device in usb.core.find(find_all=True):
    print(f"ID {device.idVendor:04x}:{device.idProduct:04x} - {device.manufacturer} {device.product}")