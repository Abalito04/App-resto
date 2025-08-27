from flask import Flask
from flask_migrate import Migrate
from flask.cli import with_appcontext
from app import app, db

migrate = Migrate(app, db)

# Registrar los comandos de flask db
import click
from flask_migrate import upgrade, migrate as migrate_cmd, init, revision

@app.cli.command("db_init")
@with_appcontext
def db_init():
    """Inicializar migraciones"""
    init()

@app.cli.command("db_migrate")
@with_appcontext
def db_migrate():
    """Crear migración"""
    migrate_cmd(message="Auto migration")

@app.cli.command("db_upgrade")
@with_appcontext
def db_upgrade():
    """Aplicar migraciones"""
    upgrade()

if __name__ == "__main__":
    app.run()
