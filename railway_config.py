#!/usr/bin/env python3
"""
Configuración específica para Railway
"""
import os

def setup_railway_config():
    """Configurar variables de entorno para Railway"""
    try:
        # Configurar zona horaria por defecto si no está definida
        if not os.getenv('SERVER_TIMEZONE'):
            os.environ['SERVER_TIMEZONE'] = 'America/Argentina/Buenos_Aires'
        
        # Configurar Flask para producción
        if not os.getenv('FLASK_ENV'):
            os.environ['FLASK_ENV'] = 'production'
        
        # Configurar secret key si no está definida
        if not os.getenv('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'railway-secret-key-change-in-production'
        
        print("🚀 Configuración de Railway aplicada")
    except Exception as e:
        print(f"⚠️ Error en configuración de Railway: {e}")

if __name__ == '__main__':
    setup_railway_config()
