# Validación de DNI Único - Documentación

## 📋 Resumen de cambios

Se implementó un sistema robusto para evitar que se creen múltiples perfiles con el mismo DNI. Los cambios incluyen:

### 1. **Modelo de Base de Datos** (`app/models.py`)
- Campo `Perfil.dni` ahora tiene `unique=True` (máximo 20 caracteres)
- Esto garantiza a nivel de BD que no pueden existir dos perfiles con el mismo DNI

### 2. **Validación en Formularios** (`app/forms.py`)
- **`RegisterForm.clean()`**: Valida DNI duplicado antes de crear usuario
- **`PerfilUpdateForm.clean_dni()`**: Valida al editar perfil, permitiendo DNI igual al actual

### 3. **Manejo de Errores en Vistas** (`app/views.py`)
- **`register_view`**: 
  - Usa `transaction.atomic()` para garantizar que si falla la creación del `Perfil` o `Paciente`, se revierte la creación del `User`
  - Captura `IntegrityError` si por alguna razón pasa un DNI duplicado (race condition)
  - Elimina el `User` creado si ocurre un error
  - Mensajes de error amigables para el usuario

- **`mi_perfil`**:
  - Validación que el usuario tenga perfil asociado
  - Manejo de `IntegrityError` al actualizar
  - Mensajes de éxito/error claros

---

## 🔧 Instrucciones para el equipo

### Ejecutar las migraciones
Si aún no las ejecutaste (primeros cambios), corre:
```bash
# Activar entorno virtual
virtual\Scripts\activate.bat

# Aplicar migraciones
python manage.py migrate
```

### Probar el flujo de validación

#### Test 1: Intenta crear dos usuarios con el mismo DNI
1. Navega a `/registro/`
2. Crea un usuario con DNI `12345678`
3. Intenta crear otro con el mismo DNI
4. **Resultado esperado**: Se muestra error "Ya existe un usuario con ese DNI"

#### Test 2: Intenta editar perfil con DNI duplicado
1. Como usuario autenticado, ve a `/mi-perfil/`
2. Intenta cambiar tu DNI al de otro usuario existente
3. **Resultado esperado**: Se muestra error "El DNI ingresado ya está asociado a otra cuenta"

#### Test 3: Verificar no hay usuarios huérfanos
1. Simula un error durante `register_view` (interrumpe con break point)
2. Si ocurre error, el `User` debe eliminarse y no quedar sin `Perfil`
3. **Base de datos**: No debe haber `User` sin `Perfil` asociado

---

## 📊 Estructura de datos

```
User (Django built-in)
  ↓
Perfil (OneToOneField a User, con DNI unique)
  ↓
Paciente (OneToOneField a Perfil, con dni_paciente)
```

**Invariante**: `Perfil.dni` es único. No puede haber dos `Perfil` con el mismo DNI.

---

## ⚠️ Notas importantes

1. **Campo `dni`**: Permite valores vacíos (`blank=True`) pero si tiene valor, es único
2. **Regex de DNI**: No hay validación de formato (ej: solo números). Si quieres restricción, añade validador en `forms.py`
3. **Backup**: Se creó `db.sqlite3.20251123201606.bak` (copia de seguridad de la BD antes de aplicar migración)
4. **Transacciones**: Se usan para evitar inconsistencias entre `User`, `Perfil` y `Paciente`

---

## 🐛 Troubleshooting

### Error: "table app_estadisticapaciente already exists"
**Causa**: La tabla ya existía antes de crear la migración
**Solución**: Se resolvió manualmente; si ocurre de nuevo, usa:
```bash
python manage.py migrate --fake app 0005
```

### Error: IntegrityError en producción
**Causa**: Dos request llegaron simultáneamente con el mismo DNI
**Solución**: El código ya lo maneja con `transaction.atomic()` y cleanup

### DNI vacío permite duplicados
**Esperado**: `blank=True` permite vacíos múltiples. Si quieres evitar:
```python
# En Perfil.dni:
dni = models.CharField(max_length=20, default="", blank=False, unique=True)
```

---

## 📝 Comandos útiles

### Ver migraciones aplicadas
```bash
python manage.py showmigrations app
```

### Revisar cambios en DB
```bash
# Abrir SQLite
sqlite3 db.sqlite3
# Listar campos de Perfil
.schema app_perfil
# Ver si hay índice unique en dni
.index app_perfil
```

### Crear admin para gestionar perfiles
```bash
python manage.py createsuperuser
# Luego en Django admin puedes ver/editar perfiles
```

---

## 🎯 Próximos pasos (opcionales)

1. **Validación de formato DNI**: Añadir regex o validador personalizado
2. **Tests automatizados**: Crear test cases para evitar duplicados
3. **Merge de perfiles duplicados**: Si hay datos históricos duplicados, script para consolidar
4. **Logs de auditoría**: Registrar intentos fallidos de registro

---

**Última actualización**: 23 de noviembre de 2025
