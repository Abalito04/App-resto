#!/usr/bin/env python3
"""Configuracion especifica para Railway."""
import os


def setup_railway_config():
    """Configurar defaults no sensibles para Railway."""
    try:
        os.environ.setdefault("SERVER_TIMEZONE", "America/Argentina/Buenos_Aires")
        os.environ.setdefault("FLASK_ENV", "production")
        print("Configuracion de Railway aplicada")
    except Exception as e:
        print(f"Error en configuracion de Railway: {e}")


if __name__ == "__main__":
    setup_railway_config()
