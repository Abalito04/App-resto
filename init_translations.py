#!/usr/bin/env python3
"""
Script para inicializar las traducciones en Railway
"""
import os
import sys

def compile_translations():
    """Compila los archivos de traducción si no existen"""
    try:
        # Verificar si los archivos .mo existen
        es_mo = 'translations/es/LC_MESSAGES/messages.mo'
        en_mo = 'translations/en/LC_MESSAGES/messages.mo'
        
        if not os.path.exists(es_mo) or not os.path.exists(en_mo):
            print("Compilando traducciones...")
            
            try:
                # Intentar usar Babel para compilar
                from babel.messages.frontend import compile_catalog
                
                # Compilar español
                if os.path.exists('translations/es/LC_MESSAGES/messages.po'):
                    compile_catalog('translations/es/LC_MESSAGES/messages.po', 
                                  'translations/es/LC_MESSAGES/messages.mo')
                    print("✅ Traducciones en español compiladas con Babel")
                
                # Compilar inglés
                if os.path.exists('translations/en/LC_MESSAGES/messages.po'):
                    compile_catalog('translations/en/LC_MESSAGES/messages.po', 
                                  'translations/en/LC_MESSAGES/messages.mo')
                    print("✅ Traducciones en inglés compiladas con Babel")
                    
            except ImportError:
                print("⚠️ Babel no disponible, usando sistema de traducciones simple")
                # Verificar que el sistema simple esté disponible
                try:
                    import simple_translations
                    print("✅ Sistema de traducciones simple verificado")
                except ImportError:
                    print("⚠️ Sistema de traducciones simple no disponible")
        else:
            print("✅ Traducciones ya compiladas")
            
    except Exception as e:
        print(f"⚠️ Error compilando traducciones: {e}")
        print("Continuando sin compilar...")

if __name__ == '__main__':
    compile_translations()
