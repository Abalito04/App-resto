#!/usr/bin/env python3
"""
Sistema de traducciones simple como fallback si Babel no está disponible
"""
import os

# Diccionario de traducciones
TRANSLATIONS = {
    'es': {
        # Navegación
        'Mozo': 'Mozo',
        'Cocina': 'Cocina',
        'Historial': 'Historial',
        'Configuración': 'Configuración',
        'Planes': 'Planes',
        'Panel de Usuarios': 'Panel de Usuarios',
        'Admin Planes': 'Admin Planes',
        'Mi Perfil': 'Mi Perfil',
        'Cerrar Sesión': 'Cerrar Sesión',
        'Iniciar Sesión': 'Iniciar Sesión',
        'Registrarse': 'Registrarse',
        
        # Dashboard
        'Tomar pedido': 'Tomar pedido',
        'Tipo de consumo:': 'Tipo de consumo:',
        'En el local': 'En el local',
        'Para llevar': 'Para llevar',
        'Mesa:': 'Mesa:',
        'Nombre Cliente:': 'Nombre Cliente:',
        'Dirección:': 'Dirección:',
        'Método de pago:': 'Método de pago:',
        'Efectivo': 'Efectivo',
        'Transferencia': 'Transferencia',
        'Deuda': 'Deuda',
        'Tarjeta': 'Tarjeta',
        'N° de Ticket:': 'N° de Ticket:',
        'Titular:': 'Titular:',
        'Productos:': 'Productos:',
        'Seleccionar': 'Seleccionar',
        'Agregar pedido': 'Agregar pedido',
        'Pedidos activos': 'Pedidos activos',
        'No hay pedidos activos.': 'No hay pedidos activos.',
        'Editar': 'Editar',
        'Borrar': 'Borrar',
        'Entregado': 'Entregado',
        'Gestionar productos': 'Gestionar productos',
        'Nombre': 'Nombre',
        'Precio': 'Precio',
        'Agregar producto': 'Agregar producto',
        'Acciones': 'Acciones',
        'Guardar': 'Guardar',
        
        # Cocina
        'Cocina - Pedidos activos': 'Cocina - Pedidos activos',
        'Para llevar:': 'Para llevar:',
        'Fecha:': 'Fecha:',
        'Hora local': 'Hora local',
        'Tiempo en cocina:': 'Tiempo en cocina:',
        'Pendiente de recibir en cocina': 'Pendiente de recibir en cocina',
        'Recibir en cocina': 'Recibir en cocina',
        'No hay pedidos pendientes.': 'No hay pedidos pendientes.',
        
        # Historial
        'Historial de pedidos': 'Historial de pedidos',
        'Última semana': 'Última semana',
        'Último mes': 'Último mes',
        'Todos': 'Todos',
        'Consumo:': 'Consumo:',
        'No hay pedidos para este filtro.': 'No hay pedidos para este filtro.',
        
        # Login
        'Ingresar': 'Ingresar',
        'Email': 'Email',
        'Contraseña': 'Contraseña',
        'Entrar': 'Entrar',
        '¿No recibiste el email de confirmación?': '¿No recibiste el email de confirmación?',
        
        # Modal
        'Detalles del pedido': 'Detalles del pedido',
        'Cerrar': 'Cerrar',
        'Cliente:': 'Cliente:',
        'Método de pago:': 'Método de pago:',
        'Ticket:': 'Ticket:',
        'Comprobante:': 'Comprobante:',
        'Deudor:': 'Deudor:',
        
        # Errores
        'Debe ingresar el número de mesa': 'Debe ingresar el número de mesa',
        'Debes iniciar sesión para acceder.': 'Debes iniciar sesión para acceder.',
        
        # Títulos
        'Resto App': 'Resto App',
        'Plan': 'Plan',
        'Conectado': 'Conectado',
        'Sin conexión': 'Sin conexión',
        'Cambiar tema': 'Cambiar tema',
        'Cambiar idioma': 'Cambiar idioma',
        'Idioma': 'Idioma',
        'Español': 'Español',
        'English': 'English',
        
        # Administración de Planes
        'Administración de Planes': 'Administración de Planes',
        'Planes Disponibles': 'Planes Disponibles',
        'Restaurantes y Planes Actuales': 'Restaurantes y Planes Actuales',
        'Restaurante': 'Restaurante',
        'Plan Actual': 'Plan Actual',
        'Uso': 'Uso',
        'Acciones': 'Acciones',
        'Cambiar Plan': 'Cambiar Plan',
        'Productos': 'Productos',
        'Usuarios': 'Usuarios',
        'Pedidos/día': 'Pedidos/día',
        'Eliminar Restaurante': 'Eliminar Restaurante',
        '¿Estás seguro de que quieres eliminar este restaurante?': '¿Estás seguro de que quieres eliminar este restaurante?',
        'Esta acción no se puede deshacer': 'Esta acción no se puede deshacer',
        'Restaurante eliminado exitosamente': 'Restaurante eliminado exitosamente',
        'Error al eliminar restaurante': 'Error al eliminar restaurante'
    },
    'en': {
        # Navigation
        'Mozo': 'Waiter',
        'Cocina': 'Kitchen',
        'Historial': 'History',
        'Configuración': 'Settings',
        'Planes': 'Plans',
        'Panel de Usuarios': 'User Panel',
        'Admin Planes': 'Admin Plans',
        'Mi Perfil': 'My Profile',
        'Cerrar Sesión': 'Logout',
        'Iniciar Sesión': 'Login',
        'Registrarse': 'Register',
        
        # Dashboard
        'Tomar pedido': 'Take Order',
        'Tipo de consumo:': 'Consumption type:',
        'En el local': 'Dine in',
        'Para llevar': 'Take away',
        'Mesa:': 'Table:',
        'Nombre Cliente:': 'Customer Name:',
        'Dirección:': 'Address:',
        'Método de pago:': 'Payment method:',
        'Efectivo': 'Cash',
        'Transferencia': 'Transfer',
        'Deuda': 'Debt',
        'Tarjeta': 'Card',
        'N° de Ticket:': 'Ticket #:',
        'Titular:': 'Cardholder:',
        'Productos:': 'Products:',
        'Seleccionar': 'Select',
        'Agregar pedido': 'Add Order',
        'Pedidos activos': 'Active Orders',
        'No hay pedidos activos.': 'No active orders.',
        'Editar': 'Edit',
        'Borrar': 'Delete',
        'Entregado': 'Delivered',
        'Gestionar productos': 'Manage Products',
        'Nombre': 'Name',
        'Precio': 'Price',
        'Agregar producto': 'Add Product',
        'Acciones': 'Actions',
        'Guardar': 'Save',
        
        # Kitchen
        'Cocina - Pedidos activos': 'Kitchen - Active Orders',
        'Para llevar:': 'Take away:',
        'Fecha:': 'Date:',
        'Hora local': 'Local time',
        'Tiempo en cocina:': 'Time in kitchen:',
        'Pendiente de recibir en cocina': 'Pending kitchen reception',
        'Recibir en cocina': 'Receive in kitchen',
        'No hay pedidos pendientes.': 'No pending orders.',
        
        # History
        'Historial de pedidos': 'Order History',
        'Última semana': 'Last week',
        'Último mes': 'Last month',
        'Todos': 'All',
        'Consumo:': 'Consumption:',
        'No hay pedidos para este filtro.': 'No orders for this filter.',
        
        # Login
        'Ingresar': 'Sign In',
        'Email': 'Email',
        'Contraseña': 'Password',
        'Entrar': 'Enter',
        '¿No recibiste el email de confirmación?': "Didn't receive confirmation email?",
        
        # Modal
        'Detalles del pedido': 'Order Details',
        'Cerrar': 'Close',
        'Cliente:': 'Customer:',
        'Método de pago:': 'Payment method:',
        'Ticket:': 'Ticket:',
        'Comprobante:': 'Receipt:',
        'Deudor:': 'Debtor:',
        
        # Errors
        'Debe ingresar el número de mesa': 'Must enter table number',
        'Debes iniciar sesión para acceder.': 'You must log in to access.',
        
        # Titles
        'Resto App': 'Resto App',
        'Plan': 'Plan',
        'Conectado': 'Connected',
        'Sin conexión': 'Offline',
        'Cambiar tema': 'Change theme',
        'Cambiar idioma': 'Change language',
        'Idioma': 'Language',
        'Español': 'Spanish',
        'English': 'English',
        
        # Plan Administration
        'Administración de Planes': 'Plan Administration',
        'Planes Disponibles': 'Available Plans',
        'Restaurantes y Planes Actuales': 'Restaurants and Current Plans',
        'Restaurante': 'Restaurant',
        'Plan Actual': 'Current Plan',
        'Uso': 'Usage',
        'Acciones': 'Actions',
        'Cambiar Plan': 'Change Plan',
        'Productos': 'Products',
        'Usuarios': 'Users',
        'Pedidos/día': 'Orders/day',
        'Eliminar Restaurante': 'Delete Restaurant',
        '¿Estás seguro de que quieres eliminar este restaurante?': 'Are you sure you want to delete this restaurant?',
        'Esta acción no se puede deshacer': 'This action cannot be undone',
        'Restaurante eliminado exitosamente': 'Restaurant deleted successfully',
        'Error al eliminar restaurante': 'Error deleting restaurant'
    }
}

def get_translation(text, locale='es'):
    """Obtiene la traducción de un texto"""
    if locale in TRANSLATIONS and text in TRANSLATIONS[locale]:
        return TRANSLATIONS[locale][text]
    return text  # Retorna el texto original si no hay traducción

def get_available_languages():
    """Retorna los idiomas disponibles"""
    return list(TRANSLATIONS.keys())
