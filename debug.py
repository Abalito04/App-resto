# debug.py - Ver qué error específico está causando el 500
import traceback
from app import app, db
from models import Usuario

# Activar debug mode
app.config['DEBUG'] = True

def test_database():
    """Probar conexión a base de datos"""
    try:
        with app.app_context():
            # Probar consulta simple
            usuarios = Usuario.query.count()
            print(f"✅ Base de datos funciona. Usuarios: {usuarios}")
            return True
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")
        traceback.print_exc()
        return False

def test_templates():
    """Probar que los templates existen"""
    import os
    
    templates = [
        'templates/setup.html',
        'templates/auth/login.html', 
        'templates/auth/registro.html',
        'templates/auth/configuracion.html'
    ]
    
    for template in templates:
        if os.path.exists(template):
            print(f"✅ {template} existe")
        else:
            print(f"❌ {template} NO EXISTE")

def test_imports():
    """Probar imports"""
    try:
        from auth import crear_slug
        print("✅ Import de crear_slug funciona")
        
        from models import Usuario, Restaurante
        print("✅ Imports de models funcionan")
        
        return True
    except Exception as e:
        print(f"❌ Error de imports: {e}")
        traceback.print_exc()
        return False

def test_routes():
    """Probar rutas básicas"""
    try:
        with app.test_client() as client:
            # Probar ruta principal
            response = client.get('/')
            print(f"✅ Ruta / responde con código: {response.status_code}")
            
            # Probar setup
            response = client.get('/setup')
            print(f"✅ Ruta /setup responde con código: {response.status_code}")
            
            return True
    except Exception as e:
        print(f"❌ Error en rutas: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE ERRORES")
    print("=" * 50)
    
    print("\n1. Probando imports...")
    test_imports()
    
    print("\n2. Verificando templates...")
    test_templates()
    
    print("\n3. Probando base de datos...")
    test_database()
    
    print("\n4. Probando rutas...")
    test_routes()
    
    print("\n✅ Diagnóstico completado")
    
    # Ejecutar app en modo debug
    print("\n🚀 Iniciando app en modo debug...")
    app.run(debug=True, port=5001)