# 📧 Configurar Template de EmailJS Correctamente

## 🚨 **Error Identificado: "The recipients address is empty"**

Este error indica que EmailJS no puede encontrar la dirección de email del destinatario en los parámetros.

## 🔧 **Solución: Configurar Template Correctamente**

### **Paso 1: Verificar Configuración del Template**

En tu dashboard de EmailJS:

1. **Ve a Email Templates**
2. **Selecciona tu template** `template_mg7eult`
3. **Verifica la configuración** del template

### **Paso 2: Configurar Recipients**

En la sección **"Recipients"** del template:

#### **Opción A: Usar Variable (Recomendado)**
- **To Email**: `{{to_email}}`
- **To Name**: `{{to_name}}`

#### **Opción B: Usar Email Fijo**
- **To Email**: `{{user_email}}` o `{{reply_to}}`
- **To Name**: `{{to_name}}`

### **Paso 3: Configurar From**

En la sección **"From"**:
- **From Email**: `abalito95@gmail.com`
- **From Name**: `{{from_name}}`

### **Paso 4: Configurar Subject**

En la sección **"Subject"**:
```
Confirma tu cuenta - Sistema de Restaurantes
```

### **Paso 5: Configurar Content**

En la sección **"Content"** (HTML):

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

## 🧪 **Template de Prueba Simple**

Si el template complejo no funciona, crea uno simple:

### **Configuración Simple:**
- **Template ID**: `template_simple`
- **To Email**: `{{to_email}}`
- **To Name**: `{{to_name}}`
- **From Email**: `abalito95@gmail.com`
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
// Cambiar temporalmente en login.html línea 87
emailjs.send('service_yj1mcpr', 'template_simple', templateParams)
```

## 📊 **Verificación de Configuración**

### **Checklist del Template:**
- ✅ **Template está publicado** (no en draft)
- ✅ **To Email configurado** con `{{to_email}}`
- ✅ **To Name configurado** con `{{to_name}}`
- ✅ **From Email configurado** con tu email
- ✅ **Subject configurado**
- ✅ **Content configurado** con variables correctas

### **Checklist del Servicio:**
- ✅ **Service está activo**
- ✅ **Email de envío configurado** correctamente
- ✅ **Autenticación funcionando**

## 🎯 **Resultado Esperado**

Con la configuración correcta, deberías ver:

```
=== DIAGNÓSTICO EMAILJS ===
Credenciales:
- Service ID: service_yj1mcpr
- Template ID: template_mg7eult
- Public Key: 79cmvTkckyQwZrWM7

Parámetros enviados:
- to_email: abalito0495@gmail.com
- to_name: mati
- confirm_url: http://app-resto.up.railway.app/auth/confirmar/STmFZxiYFncOynNJXQuOcdY8u321Wln5Y9lVLzIisCs
- restaurante: mati
- from_name: Sistema de Restaurantes
- reply_to: abalito0495@gmail.com
- user_email: abalito0495@gmail.com

✅ Email enviado exitosamente: 200 OK
```

## 🚨 **Si Persiste el Error**

1. **Crea un template simple** para probar
2. **Verifica que el servicio esté activo**
3. **Confirma que el template esté publicado**
4. **Prueba con parámetros mínimos**

---

**¿Necesitas ayuda?** Comparte una captura de pantalla de la configuración de tu template en EmailJS.
