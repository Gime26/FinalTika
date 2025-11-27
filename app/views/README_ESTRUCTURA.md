# Reorganización de Views - FinalTika

## 📁 Estructura Modular

El archivo monolítico `views.py` (1695 líneas) ha sido reorganizado en una estructura modular para mejor mantenibilidad:

```
app/views/
├── __init__.py                 # Punto de entrada - importa todas las vistas
├── auth_views.py               # Autenticación y registro
├── perfil_views.py             # Gestión de perfiles de usuario
├── dashboard_views.py          # Dashboards y página de inicio
├── turno_views.py              # Sistema de turnos/citas
├── paciente_views.py           # CRUD de pacientes
├── observacion_views.py        # Observaciones clínicas
├── testimonio_views.py         # Testimonios públicos y gestión
├── contacto_views.py           # Mensajes de contacto
├── informe_views.py            # Informes interdisciplinarios
├── entrevista_views.py         # Entrevistas de admisión
├── estadistica_views.py        # Estadísticas
└── comprobantes_views.py       # Comprobantes
```

## 🔄 Retrocompatibilidad

**No se requieren cambios en `urls.py`** - todos los imports siguen funcionando exactamente igual:

```python
from app.views import login_view, dashboard, crear_turno, ...
```

El archivo `__init__.py` re-exporta todas las funciones usando `from .module import *`.

## 📋 Detalle de Módulos

### auth_views.py (3 funciones)
- `login_view` - Login con redirección según rol
- `register_view` - Registro de usuarios
- `base` - Vista base (legacy)

### perfil_views.py (2 funciones)
- `mi_perfil` - Ver perfil del usuario
- `editar_perfil` - Editar datos del perfil

### dashboard_views.py (4 funciones)
- `inicio` - Página de inicio con formulario de contacto
- `dashboard` - Dashboard de especialistas
- `dashboard_terapeutas` - Dashboard de terapeutas (legacy)
- `dashboard_pacientes` - Dashboard de pacientes (importada de paciente_views)

### turno_views.py (7 funciones)
- `gestion_turnos` - Vista principal de gestión
- `crear_turno` - Crear nuevo turno (AJAX/JSON) **[CRÍTICO - recientemente arreglado]**
- `editar_turno` - Modificar turno existente
- `confirmar_turno` - Confirmar cita
- `cancelar_turno` - Cancelar cita
- `eliminar_turno` - Eliminar permanentemente
- `turnos_view`, `gestionturnos` - Redirects legacy

### paciente_views.py (10 funciones)
- `pacientes_list` - Listar todos los pacientes
- `paciente_create` - Crear nuevo paciente
- `paciente_update` - Editar paciente
- `paciente_delete` - Eliminar paciente
- `dashboard_pacientes` - Dashboard de pacientes
- `paciente_turnos` - Ver turnos del paciente
- `paciente_informes` - Ver informes del paciente
- `paciente_observaciones` - Ver observaciones
- `paciente_comprobantes` - Ver comprobantes
- `paciente_perfil` - Ver perfil

### observacion_views.py (4 funciones)
- `ListaObservacionesView` - ListView de observaciones
- `CrearObservacionView` - CreateView con auto-asignación
- `editar_observacion` - Editar observación
- `eliminar_observacion` - Eliminar observación

### testimonio_views.py (8 funciones)
- `enviar_testimonio` - Formulario público
- `testimonios_publicos` - Lista pública de testimonios aprobados
- `testimonios_lista` - Gestión de testimonios (dashboard)
- `aprobar_testimonio` - Aprobar para publicación
- `restringir_testimonio` - Restringir testimonio
- `editar_testimonio` - Editar contenido
- `eliminar_testimonio` - Eliminar permanentemente
- `testimonios_inicio` - Testimonios en página inicio

### contacto_views.py (5 funciones)
- `lista_contactos` - Ver todos los mensajes
- `marcar_contacto_leido` - Cambiar estado a "leído"
- `marcar_contacto_respondido` - Cambiar estado a "respondido"
- `confirmar_eliminar_contacto` - Vista de confirmación
- `eliminar_contacto` - Eliminar mensaje

### informe_views.py (7 funciones)
- `crear_informe_interdisciplinario` - Nuevo informe
- `lista_informes` - Ver todos los informes
- `detalle_informe` - Ver informe completo con secciones
- `agregar_seccion_informe` - Especialista agrega su sección
- `editar_informe` - Editar informe base
- `eliminar_informe` - Eliminar informe completo
- `eliminar_seccion_informe` - Eliminar sección específica

### entrevista_views.py (4 funciones)
- `entrevista_view` - Formulario público de admisión
- `gestion_entrevistas` - Dashboard de entrevistas
- `ver_entrevista` - Ver detalle completo
- `derivar_entrevista` - Asignar especialista y cambiar estado

### estadistica_views.py (2 funciones)
- `estadistica_view` - Ver estadísticas
- `estadistica_agregar` - Agregar datos (AJAX)

### comprobantes_views.py (1 función)
- `comprobantes_view` - Vista de comprobantes

## ✅ Beneficios

1. **Mantenibilidad**: Cada módulo tiene < 250 líneas, fácil de navegar
2. **Separación de responsabilidades**: Cada archivo tiene un propósito claro
3. **Búsqueda rápida**: Sabés exactamente dónde buscar una función
4. **Testing**: Más fácil testear módulos individuales
5. **Colaboración**: Menos conflictos de merge en git
6. **Documentación**: Cada módulo tiene docstrings claros

## 🔍 Cómo Encontrar una Vista

**Antes** (1695 líneas):
- Buscar en archivo gigante con Ctrl+F
- Scroll interminable

**Ahora**:
1. ¿Turnos? → `turno_views.py`
2. ¿Pacientes? → `paciente_views.py`
3. ¿Login? → `auth_views.py`
4. ¿Testimonios? → `testimonio_views.py`

## 🗄️ Archivo Original

El archivo original ha sido respaldado como:
- `app/views_old_backup.py` (1695 líneas)

**NO ELIMINAR** hasta verificar que todo funciona correctamente en producción.

## 🧪 Testing

```bash
# Verificar que no hay errores de configuración
python manage.py check

# Verificar que las importaciones funcionan
python manage.py shell
>>> from app.views import login_view, crear_turno, dashboard
>>> # Si no hay errores, todo está bien

# Correr el servidor
python manage.py runserver 0.0.0.0:8000
```

## 📝 Notas Importantes

1. **crear_turno** en `turno_views.py`: Esta función usa `@csrf_exempt` con validación manual de autenticación para funcionar con AJAX/JSON. NO cambiar a `@login_required` sin ajustar el frontend.

2. **Todas las vistas mantienen**:
   - Decoradores originales (`@login_required`, `@solo_terapeutas`, etc.)
   - Lógica de permisos
   - Validaciones
   - Mensajes al usuario

3. **__all__**: Cada módulo define `__all__` para exportación explícita

## 🚀 Próximos Pasos

- ✅ Estructura modular creada
- ✅ Imports funcionando correctamente
- ✅ Django check sin errores
- ⏳ Testing en desarrollo (localhost)
- ⏳ Testing en producción
- ⏳ Eliminar `views_old_backup.py` después de 1 semana sin issues

---

**Fecha de reorganización**: 2025
**Motivo**: Archivo monolítico de 1695 líneas dificultaba mantenimiento
**Resultado**: 12 módulos organizados por funcionalidad
