# 🔍 Verificar Template de EmailJS

## 📋 **Checklist de Verificación**

### **1. Verificar Template en Dashboard**

Ve a tu dashboard de EmailJS y verifica:

#### **Template Settings:**
- ✅ **Template ID**: `template_mg7eult`
- ✅ **Template Name**: Cualquier nombre que hayas puesto
- ✅ **Status**: Debe estar **"Published"** (no Draft)

#### **Template Content:**
Verifica que tu template HTML use exactamente estos nombres de variables:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Confirmación de Cuenta</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
        <h2 style="color: #333; text-align: center;">¡Bienvenido! 🍽️</h2>
        
        <p>Hola {{to_name}},</p>
        
        <p>Para activar tu cuenta, haz clic en el siguiente botón:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{confirm_url}}" style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Confirmar Cuenta</a>
        </div>
        
        <p>Si no puedes hacer clic en el botón, copia y pega este enlace:</p>
        <p style="word-break: break-all; background-color: #e9ecef; padding: 10px; border-radius: 3px; font-family: monospace;">{{confirm_url}}</p>
        
        <p><strong>Restaurante:</strong> {{restaurante}}</p>
        
        <p>¡Gracias por unirte a nosotros!</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
        <p style="color: #666; font-size: 12px; text-align: center;">
            {{from_name}}<br>
            Sistema de Gestión de Restaurantes
        </p>
    </div>
</body>
</html>
```

### **2. Verificar Service Configuration**

#### **Service Settings:**
- ✅ **Service ID**: `service_yj1mcpr`
- ✅ **Service Name**: Cualquier nombre que hayas puesto
- ✅ **Status**: Debe estar **"Active"**

#### **Email Configuration:**
- ✅ **From Email**: `abalito95@gmail.com`
- ✅ **From Name**: `Sistema de Restaurantes` (opcional)

### **3. Verificar Account Settings**

#### **General Settings:**
- ✅ **Public Key**: `79cmvTkckyQwZrWM7`
- ✅ **Account Status**: Active

## 🧪 **Template de Prueba Simple**

Si el template complejo no funciona, crea uno simple para probar:

### **Nuevo Template:**
- **Template ID**: `template_simple`
- **Subject**: `Prueba de Email`

### **Contenido Simple:**
```html
Hola {{to_name}},

Tu email: {{to_email}}
Enlace: {{confirm_url}}

Saludos,
{{from_name}}
```

### **Código de Prueba:**
```javascript
// Cambiar temporalmente en login.html
emailjs.send('service_yj1mcpr', 'template_simple', templateParams)
```

## 🚨 **Problemas Comunes**

### **Error: "Template not found"**
- ✅ Verifica que el Template ID sea exacto
- ✅ Asegúrate de que esté publicado (no en draft)

### **Error: "Service not found"**
- ✅ Verifica que el Service ID sea exacto
- ✅ Asegúrate de que el servicio esté activo

### **Error: "Invalid parameters"**
- ✅ Verifica que los nombres de variables coincidan exactamente
- ✅ Asegúrate de que no haya espacios extra en los nombres

### **Error: "Authentication failed"**
- ✅ Verifica que la Public Key sea correcta
- ✅ Asegúrate de que no haya espacios extra

## 📊 **Logs Esperados**

Con la configuración correcta, deberías ver:

```
=== DIAGNÓSTICO EMAILJS ===
Credenciales:
- Service ID: service_yj1mcpr
- Template ID: template_mg7eult
- Public Key: 79cmvTkckyQwZrWM7

Parámetros enviados:
- to_email: usuario@ejemplo.com
- to_name: Nombre Usuario
- confirm_url: https://tu-app.railway.app/auth/confirmar/token
- restaurante: Nombre Restaurante
- from_name: Sistema de Restaurantes

✅ Email enviado exitosamente: 200 OK
```

## 🎯 **Próximos Pasos**

1. **Verifica tu template** en el dashboard de EmailJS
2. **Asegúrate de que esté publicado**
3. **Prueba el registro** de un nuevo usuario
4. **Revisa los logs** en la consola
5. **Si persiste el error**, crea un template simple para probar

---

**¿Necesitas ayuda?** Comparte una captura de pantalla de tu template en EmailJS para verificar la configuración.
