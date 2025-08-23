# App-resto
App para restaurante
# Restaurant App 🍽️

Aplicación web para la gestión de pedidos de un restaurante. Permite a los mozos tomar pedidos, ver pedidos activos, registrar el método de pago y gestionar la cocina, incluyendo historial de pedidos entregados.

---

## Tecnologías utilizadas

- **Python 3**
- **Flask**: Framework web
- **Flask-SQLAlchemy**: ORM para SQLite
- **SQLite**: Base de datos ligera
- **HTML / CSS / Bootstrap 5**: Frontend básico

---

## Funcionalidades

### Para mozo
- Crear un nuevo pedido indicando:
  - Mesa
  - Productos
  - Método de pago (Efectivo, Transferencia, Deuda)
- Ver pedidos activos con:
  - Lista de productos por pedido
  - Tiempo transcurrido desde que se creó
  - Total de la cuenta
- Editar o eliminar pedidos activos
- Marcar pedidos como **Entregado** (removiéndolos de la lista activa)

### Para cocina
- Ver lista de pedidos activos ordenados por fecha
- Marcar pedidos como **Entregado**
- Botones para eliminar pedidos si es necesario

### Historial
- Ver todos los pedidos entregados
- Visualización de productos, total y método de pago

---

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate


pip install -r requirements.txt

restaurant_app/
│
├── app.py                 # Archivo principal con rutas y lógica
├── models.py              # Definición de modelos de la base de datos
├── restaurant.db          # Base de datos SQLite (se genera automáticamente)
├── templates/             # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── cocina.html
│   ├── editar.html
│   └── historial.html
├── static/                # Archivos CSS, JS, imágenes
├── requirements.txt       # Dependencias de Python
└── README.md
