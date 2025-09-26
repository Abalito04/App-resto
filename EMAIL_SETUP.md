# 📧 Configuración de Email para Railway

## 🚨 **Problema Actual**
El sistema de registro de usuarios no puede enviar emails de confirmación porque las variables de entorno de email no están configuradas en Railway.

## ✅ **Solución: Configurar Variables de Email**

### **Opción 1: Gmail (Recomendado)**

1. **Crear una cuenta de Gmail** o usar una existente
2. **Habilitar la verificación en 2 pasos** en tu cuenta de Google
3. **Generar una contraseña de aplicación**:
   - Ve a [myaccount.google.com](https://myaccount.google.com)
   - Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones
   - Genera una contraseña para "Mail"

4. **Configurar en Railway**:
   ```
   MAIL_DEFAULT_SENDER = tu-email@gmail.com
   MAIL_USERNAME = tu-email@gmail.com
   MAIL_PASSWORD = tu-contraseña-de-aplicacion
   MAIL_SERVER = smtp.gmail.com
   MAIL_PORT = 465
   MAIL_USE_SSL = true
   MAIL_USE_TLS = false
   ```

### **Opción 2: SendGrid (Alternativa)**

1. **Crear cuenta en SendGrid** ([sendgrid.com](https://sendgrid.com))
2. **Obtener API Key** desde el dashboard
3. **Configurar en Railway**:
   ```
   SENDGRID_API_KEY = tu-api-key-de-sendgrid
   ```

## 🔧 **Cómo Configurar en Railway**

### **Método 1: Desde el Dashboard de Railway**
1. Ve a tu proyecto en [railway.app](https://railway.app)
2. Selecciona tu servicio
3. Ve a la pestaña **"Variables"**
4. Agrega las variables:
   - `MAIL_DEFAULT_SENDER` = tu-email@gmail.com
   - `MAIL_USERNAME` = tu-email@gmail.com
   - `MAIL_PASSWORD` = tu-contraseña-de-aplicacion
   - `MAIL_SERVER` = smtp.gmail.com
   - `MAIL_PORT` = 465
   - `MAIL_USE_SSL` = true
   - `MAIL_USE_TLS` = false

### **Método 2: Desde la CLI de Railway**
```bash
railway variables set MAIL_DEFAULT_SENDER=tu-email@gmail.com
railway variables set MAIL_USERNAME=tu-email@gmail.com
railway variables set MAIL_PASSWORD=tu-contraseña-de-aplicacion
railway variables set MAIL_SERVER=smtp.gmail.com
railway variables set MAIL_PORT=465
railway variables set MAIL_USE_SSL=true
railway variables set MAIL_USE_TLS=false
```

## 🧪 **Verificar Configuración**

Después de configurar las variables:

1. **Reinicia la aplicación** en Railway
2. **Intenta registrar un nuevo usuario**
3. **Revisa los logs** de Railway para ver:
   ```
   📧 Intentando enviar email de confirmación a: usuario@ejemplo.com
   📧 Usuario configurado: tu-email@gmail.com
   📧 Password configurado: Sí
   📧 Intentando conectar a smtp.gmail.com:587
   ✅ Email enviado exitosamente usando TLS
   ```

## 🚨 **Troubleshooting**

### **Error: "Variables de email no configuradas"**
- ✅ Verifica que `MAIL_USERNAME` y `MAIL_PASSWORD` estén configuradas
- ✅ Reinicia la aplicación después de agregar las variables

### **Error: "Authentication failed"**
- ✅ Verifica que la contraseña sea la **contraseña de aplicación** de Gmail
- ✅ Asegúrate de que la verificación en 2 pasos esté habilitada

### **Error: "Connection timeout"**
- ✅ Railway puede tener restricciones de red
- ✅ Considera usar SendGrid como alternativa

## 📋 **Variables Requeridas**

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `MAIL_DEFAULT_SENDER` | Email del remitente | `mi-restaurante@gmail.com` |
| `MAIL_USERNAME` | Email del remitente | `mi-restaurante@gmail.com` |
| `MAIL_PASSWORD` | Contraseña de aplicación | `abcd efgh ijkl mnop` |
| `MAIL_SERVER` | Servidor SMTP | `smtp.gmail.com` |
| `MAIL_PORT` | Puerto SMTP | `465` |
| `MAIL_USE_SSL` | Usar SSL | `true` |
| `MAIL_USE_TLS` | Usar TLS | `false` |

## 🎯 **Resultado Esperado**

Una vez configurado correctamente:
- ✅ Los usuarios recibirán emails de confirmación
- ✅ Las cuentas se activarán automáticamente al hacer clic en el enlace
- ✅ Los logs mostrarán confirmación de envío exitoso

---

**¿Necesitas ayuda?** Revisa los logs de Railway para ver mensajes detallados sobre el proceso de envío de emails.
