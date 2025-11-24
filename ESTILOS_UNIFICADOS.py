# Script para unificar estilos lilas en todos los templates
# Este archivo documenta los cambios que se deben aplicar

COLORES_TIKA = {
    'primary': '#8b5a9e',
    'primary_hover': '#7a4d8a', 
    'primary_dark': '#610455',
    'success': '#8b5a9e',
    'warning': '#c77dff',
    'danger': '#d946a6',
    'info': '#9d4edd',
    'bg_light': '#f6e8fa',
    'border': '#d4b5e0',
}

# Reemplazos a aplicar en todos los templates:
REPLACEMENTS = {
    # Colores Bootstrap -> Tika
    '#28a745': '#8b5a9e',  # green -> primary
    '#218838': '#7a4d8a',  # green-hover -> primary-hover
    '#ffc107': '#c77dff',  # yellow -> warning
    '#e0a800': '#b45fff',  # yellow-hover -> warning-hover
    '#dc3545': '#d946a6',  # red -> danger
    '#c82333': '#c23594',  # red-hover -> danger-hover
    '#007bff': '#9d4edd',  # blue -> info
    '#0056b3': '#8934d4',  # blue-hover -> info-hover
    
    # Backgrounds
    '#f8f9fa': '#f6e8fa',  # gray -> lila claro
    '#e9ecef': '#e1b9eb',  # gray -> lila medio
    
    # Borders
    '#dee2e6': '#d4b5e0',  # gray border -> lila border
    '#ced4da': '#d4b5e0',  # input border -> lila border
    
    # Text colors
    '#333': '#2d1b35',      # text dark
    '#495057': '#4a2f52',   # text medium
    '#6c757d': '#8e7a95',   # text muted
}

# Archivos que necesitan actualización:
FILES_TO_UPDATE = [
    'app/templates/observaciones/observacion_form.html',
    'app/templates/observaciones/observacion_confirm_delete.html',
    'app/templates/informes/lista_informes.html',
    'app/templates/informes/detalle_informe.html',
    'app/templates/informes/crear_informe.html',
    'app/templates/informes/editar_informe.html',
    'app/templates/informes/agregar_seccion.html',
    'app/templates/informes/informe_confirm_delete.html',
    'app/templates/informes/seccion_confirm_delete.html',
    'app/templates/pacientes/pacientes_list.html',
    'app/templates/pacientes/pacientes_form.html',
    'app/templates/pacientes/paciente_confirm_delete.html',
    'app/templates/dashboard.html',
    'app/templates/estadistica.html',
    'app/templates/comprobantes.html',
    'app/templates/dashboard/testimonios.html',
]

print("TIKA - Sistema de estilos unificados")
print("=" * 50)
print("\n✅ Colores principales configurados")
print(f"   Primary: {COLORES_TIKA['primary']}")
print(f"   Success: {COLORES_TIKA['success']}")
print(f"   Warning: {COLORES_TIKA['warning']}")
print(f"   Danger: {COLORES_TIKA['danger']}")
print(f"   Info: {COLORES_TIKA['info']}")
print("\n✅ Archivo CSS global creado: app/static/css/tika-global.css")
print("\n📋 Archivos pendientes de actualización:")
for f in FILES_TO_UPDATE:
    print(f"   - {f}")
print("\n💡 Agrega en cada template: {% load static %}")
print("   <link rel='stylesheet' href=\"{% static 'css/tika-global.css' %}\">")
