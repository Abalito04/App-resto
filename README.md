# 🍽️ App-resto

Aplicación web para la gestión de pedidos en un restaurante.  
Permite crear, administrar y visualizar pedidos en tiempo real, con soporte para historial, diferentes métodos de pago, y panel de administración para productos.

---

## ✨ Funcionalidades

- 📋 **Gestión de pedidos activos**  
  - Crear pedidos con mesa, cliente, productos y cantidades.  
  - Seleccionar método de pago: Efectivo, Transferencia, Débito/Crédito, Deuda.  
  - Campos adicionales automáticos (ejemplo: número de comprobante en Transferencia, nombre de deudor en Deuda).  
  - Estado del pedido: Activo → Entregado → Historial.  

- 🧾 **Historial de pedidos**  
  - Registro completo de pedidos entregados.  
  - Click sobre un pedido muestra **popup con detalles**:  
    - Mesa  
    - Cliente  
    - Fecha y hora  
    - Método de pago y datos adicionales  

- 🍔 **Gestión de productos**  
  - Crear nuevos productos.  
  - Editar productos existentes.  
  - Eliminar productos.  

- ⚙️ **Administración**  
  - Base de datos con **SQLite + SQLAlchemy**.  
  - Organización de frontend con **HTML + CSS + JavaScript**.  
  - Backend con **Flask (Python)**.  

---

## 🛠️ Tecnologías utilizadas

- **Python 3.x**
- **Flask**
- **SQLAlchemy**
- **SQLite**
- **HTML / CSS / JavaScript**

---

## 📦 Instalación

Cloná el repositorio:

```bash
git clone https://github.com/Abalito04/App-resto.git
cd App-resto


Creá un entorno virtual (recomendado):

python -m venv env
source env/bin/activate   # Linux/Mac
env\Scripts\activate      # Windows


Instalá las dependencias:

pip install -r requirements.txt


Inicializá la base de datos:

python
>>> from app import db
>>> db.create_all()
>>> exit()

------------------------

▶️ Uso

Iniciá la aplicación:

python app.py


Abrí en el navegador:

http://127.0.0.1:5000

------------------------
🚀 Futuras mejoras

Panel de login para administrar.

Estadísticas de ventas y reportes.

Integración con impresión de tickets.

Versión móvil con Kivy.
 
 ------------------------

Matias Abalo
📧 Contacto: abalito95@gmail.com
🌐 GitHub: Abalito04
https://abalito.dev/
