from flask import Flask
from flask_migrate import Migrate
from app import app, db  # Importamos tu app y la DB

# Inicializamos Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()
