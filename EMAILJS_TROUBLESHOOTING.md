# 🔧 Troubleshooting EmailJS - Error 422

## 🚨 **Error 422: Unprocessable Entity**

Este error indica que EmailJS no puede procesar la solicitud debido a parámetros incorrectos o faltantes.

## 🔍 **Diagnóstico Paso a Paso**

### **1. Verificar Template en EmailJS**

Ve a tu dashboard de EmailJS y verifica:

1. **Template ID**: `template_mg7eult`
2. **Service ID**: `service_yj1mcpr`
3. **Public Key**: `79cmvTkckyQwZrWM7`

### **2. Verificar Parámetros del Template**

En tu template de EmailJS, asegúrate de que uses exactamente estos nombres:

```html
<!-- En el template HTML -->
{{to_email}}
{{to_name}}
{{confirm_url}}
{{restaurante}}
{{from_name}}
```

### **3. Verificar Configuración del Servicio**

1. **Ve a Email Services** en tu dashboard
2. **Verifica que el servicio esté activo**
3. **Confirma que el email de envío sea correcto**

## 🛠️ **Soluciones Comunes**

### **Solución 1: Verificar Nombres de Parámetros**

Los nombres en el template deben coincidir exactamente con los del código:

```javascript
// ✅ Correcto
const templateParams = {
  to_email: data.email,
  to_name: data.nombre,
  confirm_url: data.confirm_url,
  restaurante: data.restaurante,
  from_name: 'Sistema de Restaurantes'
};
```

### **Solución 2: Verificar Template ID**

Asegúrate de que el Template ID sea correcto:

```javascript
// Verifica en tu dashboard de EmailJS
emailjs.send('service_yj1mcpr', 'template_mg7eult', templateParams)
//                                    ^^^^^^^^^^^^^^
//                                    Este debe coincidir
```

### **Solución 3: Verificar Service ID**

```javascript
// Verifica en tu dashboard de EmailJS
emailjs.send('service_yj1mcpr', 'template_mg7eult', templateParams)
//                    ^^^^^^^^^^^^^^
//                    Este debe coincidir
```

### **Solución 4: Verificar Public Key**

```javascript
// Verifica en tu dashboard de EmailJS
emailjs.init("79cmvTkckyQwZrWM7");
//            ^^^^^^^^^^^^^^^^^^
//            Este debe coincidir
```

## 🧪 **Prueba de Diagnóstico**

### **Template de Prueba Simple**

Crea un template de prueba con solo estos parámetros:

**Template ID**: `template_test`
**Contenido**:
```html
Hola {{to_name}},

Tu email de confirmación: {{to_email}}
Enlace: {{confirm_url}}

Saludos,
{{from_name}}
```

**Código de prueba**:
```javascript
const testParams = {
  to_email: 'tu-email@gmail.com',
  to_name: 'Test User',
  confirm_url: 'https://ejemplo.com/confirmar',
  from_name: 'Sistema Test'
};

emailjs.send('service_yj1mcpr', 'template_test', testParams)
  .then(response => console.log('Test exitoso:', response))
  .catch(error => console.error('Test falló:', error));
```

## 📊 **Logs de Debug**

Con los cambios realizados, deberías ver en la consola:

```
Verificando parámetros:
- to_email: usuario@ejemplo.com
- to_name: Nombre Usuario
- confirm_url: https://tu-app.railway.app/auth/confirmar/token
- restaurante: Nombre Restaurante
- from_name: Sistema de Restaurantes
```

## 🚨 **Errores Comunes**

### **Error: "Template not found"**
- ✅ Verifica que el Template ID sea correcto
- ✅ Asegúrate de que el template esté publicado

### **Error: "Service not found"**
- ✅ Verifica que el Service ID sea correcto
- ✅ Asegúrate de que el servicio esté activo

### **Error: "Invalid Public Key"**
- ✅ Verifica que la Public Key sea correcta
- ✅ Asegúrate de que no haya espacios extra

### **Error: "Missing required parameters"**
- ✅ Verifica que todos los parámetros del template estén en el código
- ✅ Asegúrate de que los nombres coincidan exactamente

## 🎯 **Próximos Pasos**

1. **Revisa los logs** en la consola del navegador
2. **Verifica la configuración** en tu dashboard de EmailJS
3. **Prueba con el template simple** si el complejo falla
4. **Contacta soporte de EmailJS** si el problema persiste

---

**¿Necesitas ayuda?** Comparte los logs de la consola para un diagnóstico más específico.
