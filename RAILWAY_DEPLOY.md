# 🚀 Despliegue en Railway - Guía de Configuración

## Pasos para Desplegar con Funcionalidad de Idiomas

### 1. **Preparar el Repositorio**
Asegúrate de que todos los archivos estén en el repositorio:
- ✅ `requirements.txt` (actualizado con Flask-Babel)
- ✅ `Procfile` (configurado para gunicorn)
- ✅ `runtime.txt` (Python 3.12)
- ✅ `babel.cfg` (configuración de Babel)
- ✅ `translations/` (archivos de traducción)
- ✅ `init_translations.py` (script de inicialización)
- ✅ `railway_config.py` (configuración específica)

### 2. **Variables de Entorno en Railway**
Configura estas variables en el dashboard de Railway:

```bash
# Base de datos (Railway la proporciona automáticamente)
DATABASE_URL=postgresql://...

# Configuración de la aplicación
SECRET_KEY=tu-clave-secreta-muy-segura
FLASK_ENV=production
SERVER_TIMEZONE=America/Argentina/Buenos_Aires

# Opcional: Configuración de idioma por defecto
BABEL_DEFAULT_LOCALE=es
```

### 3. **Verificar Dependencias**
El archivo `requirements.txt` incluye:
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-Migrate==4.0.7
Flask-Babel==4.0.0
Babel==2.17.0
gunicorn==21.2.0
python-dotenv==1.0.0
psycopg2-binary==2.9.7
pytz==2023.3
requests==2.31.0
```

### 4. **Proceso de Despliegue**
1. **Conectar repositorio** a Railway
2. **Configurar variables** de entorno
3. **Deploy automático** - Railway instalará dependencias
4. **Verificar logs** para confirmar que las traducciones se compilaron

### 5. **Verificación Post-Despliegue**
Una vez desplegado, verifica:
- ✅ La aplicación carga correctamente
- ✅ El botón de idioma aparece en la barra de navegación
- ✅ Se puede cambiar entre español e inglés
- ✅ Las traducciones se aplican correctamente

### 6. **Logs Importantes a Verificar**
Busca estos mensajes en los logs de Railway:

**✅ Logs de Éxito:**
```
🔧 Configurando zona horaria del servidor: America/Argentina/Buenos_Aires
✅ Zona horaria configurada: America/Argentina/Buenos_Aires
🚀 Configuración de Railway aplicada
✅ Babel inicializado correctamente
🔧 Compilando traducciones...
✅ Traducciones inicializadas
Base de datos inicializada correctamente
```

**⚠️ Logs de Fallback (también funcionan):**
```
⚠️ Error inicializando Babel: [error]
🔄 Usando sistema de traducciones simple como fallback
✅ Sistema de traducciones simple cargado
⚠️ Babel no disponible, usando sistema de traducciones simple
✅ Sistema de traducciones simple verificado
```

### 7. **Solución de Problemas**

#### Error: "No module named 'flask_login'"
- Verifica que `requirements.txt` esté actualizado
- Fuerza un redeploy en Railway
- Revisa los logs de instalación de dependencias

#### Error: "No translations found"
- Verifica que la carpeta `translations/` esté en el repositorio
- Confirma que los archivos `.mo` se compilaron correctamente
- Revisa los logs de inicialización

#### Error: "Babel configuration not found"
- Verifica que `babel.cfg` esté en la raíz del proyecto
- Confirma que la configuración de Babel esté en `app.py`

### 8. **Comandos de Railway CLI (Opcional)**
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Conectar proyecto
railway link

# Ver logs
railway logs

# Ver variables de entorno
railway variables
```

### 9. **Estructura Final del Proyecto**
```
App-resto-master/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── babel.cfg
├── railway_config.py
├── init_translations.py
├── translations/
│   ├── es/LC_MESSAGES/
│   │   ├── messages.po
│   │   └── messages.mo
│   └── en/LC_MESSAGES/
│       ├── messages.po
│       └── messages.mo
├── templates/
└── static/
```

### 10. **Funcionalidades Implementadas**
- ✅ **Cambio de idioma**: Botón en barra de navegación
- ✅ **Persistencia**: Idioma guardado en sesión
- ✅ **Traducciones completas**: Todos los templates traducidos
- ✅ **Fallback automático**: Al idioma del navegador
- ✅ **Compilación automática**: En el despliegue
- ✅ **Sistema de fallback**: Si Babel falla, usa sistema simple
- ✅ **Robustez**: Funciona con o sin Babel instalado

---

**¡Tu aplicación está lista para desplegarse en Railway con funcionalidad completa de cambio de idioma!** 🌍✨
