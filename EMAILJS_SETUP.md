# 📧 Configuración de EmailJS (Gratuito)

## 🎯 **Ventajas de EmailJS**

- ✅ **Completamente gratuito** (hasta 200 emails/mes)
- ✅ **Fácil configuración** desde el frontend
- ✅ **No requiere servidor SMTP** complejo
- ✅ **Templates HTML** profesionales
- ✅ **Múltiples proveedores** (Gmail, Outlook, etc.)

## 🚀 **Configuración Paso a Paso**

### **1. Crear cuenta en EmailJS**

1. Ve a [emailjs.com](https://www.emailjs.com/)
2. **Regístrate** con tu email
3. **Verifica tu cuenta** por email

### **2. Configurar servicio de email**

1. **Dashboard** → **Email Services**
2. **Add New Service**
3. **Selecciona tu proveedor**:
   - **Gmail** (recomendado)
   - **Outlook**
   - **Yahoo**
   - **Otros**

4. **Configura Gmail**:
   - **Service ID**: `gmail` (o el que prefieras)
   - **Email**: `abalito95@gmail.com`
   - **Password**: Tu contraseña normal de Gmail (no la de aplicación)

### **3. Crear template de email**

1. **Dashboard** → **Email Templates**
2. **Create New Template**
3. **Template ID**: `confirmacion_cuenta`
4. **Subject**: `Confirma tu cuenta - Sistema de Restaurantes`

**Contenido HTML del template:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Confirmación de Cuenta</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
        <h2 style="color: #333; text-align: center;">¡Bienvenido a nuestro sistema de gestión de restaurantes! 🍽️</h2>
        
        <p>Hola {{to_name}},</p>
        
        <p>Gracias por registrarte en nuestro sistema. Para activar tu cuenta, haz clic en el siguiente botón:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{confirm_url}}" style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Confirmar Cuenta</a>
        </div>
        
        <p>Si no puedes hacer clic en el botón, copia y pega este enlace en tu navegador:</p>
        <p style="word-break: break-all; background-color: #e9ecef; padding: 10px; border-radius: 3px; font-family: monospace;">{{confirm_url}}</p>
        
        <p><strong>Restaurante:</strong> {{restaurante}}</p>
        
        <p>¡Gracias por unirte a nosotros!</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
        <p style="color: #666; font-size: 12px; text-align: center;">
            Equipo de Soporte<br>
            Sistema de Gestión de Restaurantes
        </p>
    </div>
</body>
</html>
```

### **4. Obtener credenciales**

1. **Dashboard** → **Account** → **General**
2. **Copia tu Public Key**: `user_xxxxxxxxxxxxxxxx`
3. **Anota tu Service ID**: `gmail` (o el que creaste)
4. **Anota tu Template ID**: `confirmacion_cuenta`

### **5. Configurar en el código**

Edita `templates/auth/login.html` y reemplaza:

```javascript
// Línea 31
emailjs.init("YOUR_PUBLIC_KEY"); // Reemplazar con tu Public Key

// Línea 55
emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', templateParams)
```

**Ejemplo con tus credenciales:**
```javascript
emailjs.init("user_abc123def456ghi789");
emailjs.send('gmail', 'confirmacion_cuenta', templateParams)
```

## 🧪 **Probar la configuración**

### **1. Registro de prueba**
1. **Registra un nuevo usuario**
2. **Verifica en la consola** del navegador que no hay errores
3. **Revisa tu email** para confirmar que llega

### **2. Logs esperados**
```javascript
// En la consola del navegador:
Email enviado exitosamente: 200 OK
```

### **3. Si hay errores**
```javascript
// Verificar en la consola:
- "Error enviando email: [detalles]"
- "Error obteniendo datos del email: [detalles]"
```

## 🔧 **Troubleshooting**

### **Error: "Invalid Public Key"**
- ✅ Verifica que copiaste correctamente la Public Key
- ✅ Asegúrate de que no hay espacios extra

### **Error: "Service not found"**
- ✅ Verifica que el Service ID sea correcto
- ✅ Asegúrate de que el servicio esté activo

### **Error: "Template not found"**
- ✅ Verifica que el Template ID sea correcto
- ✅ Asegúrate de que el template esté publicado

### **Email no llega**
- ✅ Revisa la carpeta de spam
- ✅ Verifica que el email de destino sea correcto
- ✅ Asegúrate de que el servicio de email esté configurado correctamente

## 📊 **Límites de EmailJS**

| Plan | Emails/mes | Precio |
|------|------------|--------|
| Free | 200 | $0 |
| Personal | 1,000 | $15/mes |
| Business | 10,000 | $30/mes |

## 🎯 **Resultado Final**

Una vez configurado correctamente:

1. ✅ **Registro exitoso** sin crashes
2. ✅ **Email automático** enviado con EmailJS
3. ✅ **Diseño profesional** del email
4. ✅ **Confirmación de cuenta** funcionando
5. ✅ **Sistema completamente gratuito**

---

**¿Necesitas ayuda?** Revisa la consola del navegador para ver los logs detallados del proceso de envío.
