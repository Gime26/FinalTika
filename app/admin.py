from django.contrib import admin
from .models import (
    Paciente, Entrevista, Perfil, EstadoPaciente, HistorialPaciente, 
    Turno, Especialista, Centrosterapeuticos, Detallepagos, Especialidades, Especialistas, Observacion, Testimonio
)

# ----------------------
# PACIENTES
# ----------------------
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    # Esto define los campos que se muestran en el formulario "Agregar paciente"
    fields = [
        'dni', 
        'nombre', 
        'apellido', 
        'fecha_nacimiento', 
        'genero', 
        'telefono', 
        'email'
    ]
    
    # Esto define las columnas que se muestran en la lista de pacientes
    list_display = (
        'dni', 
        'nombre', 
        'apellido', 
        'fecha_nacimiento', 
        'genero', 
        'telefono', 
        'email'
    )
    
    search_fields = ('nombre', 'apellido', 'dni', 'email')
    list_filter = ('genero',)
# ----------------------
# ENTREVISTAS
# ----------------------
@admin.register(Entrevista)
class EntrevistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'fecha', 'hora', 'motivo_consulta', 'estado')
    search_fields = ('paciente__nombre', 'paciente__apellido')
    list_filter = ('fecha', 'estado')

# ----------------------
# PERFIL USUARIO
# ----------------------
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'nombre', 'apellido', 'dni', 'nacionalidad', 
        'domicilio', 'telefono', 'cp', 'email', 'especialidad', 'matricula', 'rol']
    search_fields = ['user__username', 'nombre', 'apellido', 'dni', 'matricula', 'email']
    list_filter = ['rol']
    exclude = ['paciente']  # Excluir el campo paciente del formulario de admin
    
    def get_readonly_fields(self, request, obj=None):
        # Solo hacer 'user' de solo lectura cuando se está editando (obj existe)
        # Cuando se está creando (obj es None), permitir seleccionar el usuario
        if obj:  # Editando un perfil existente
            return ['user']
        return []  # Creando un nuevo perfil, permitir seleccionar usuario
# ----------------------
# ESTADO PACIENTE
# ----------------------
@admin.register(EstadoPaciente)
class EstadoPacienteAdmin(admin.ModelAdmin):
    list_display = ('id_estado', 'nombre_estado')
    search_fields = ('nombre_estado',)

# ----------------------
# HISTORIAL PACIENTE
# ----------------------
@admin.register(HistorialPaciente)
class HistorialPacienteAdmin(admin.ModelAdmin):
    list_display = ('nro_historia_paciente', 'paciente', 'estado_paciente', 'observaciones', 'antecedentes')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'observaciones')

# ----------------------
# TURNOS Y ESPECIALISTAS
# ----------------------
@admin.register(Especialista)
class EspecialistaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad', 'matricula', 'email', 'telefono')
    search_fields = ('nombre', 'especialidad', 'matricula', 'email')
    list_filter = ('especialidad',)

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'especialista', 'fecha', 'hora', 'status', 'motivo')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'especialista__nombre', 'motivo')
    list_filter = ('fecha', 'status', 'especialista')
    ordering = ('-fecha', '-hora')

# ----------------------
# CENTROS TERAPÉUTICOS
# ----------------------
@admin.register(Centrosterapeuticos)
class CentrosterapeuticosAdmin(admin.ModelAdmin):
    list_display = ('id_centroterapeutico', 'nombre', 'telefono')
    search_fields = ('nombre',)

# ----------------------
# DETALLE PAGOS
# ----------------------
@admin.register(Detallepagos)
class DetallepagosAdmin(admin.ModelAdmin):
    list_display = ('codigo_pago', 'monto', 'observaciones')
    search_fields = ('codigo_pago',)

# Para Especialidades
@admin.register(Especialidades)
class EspecialidadesAdmin(admin.ModelAdmin):
    list_display = ('id_especialidades', 'id_especialista', 'nombre', 'matricula')
    search_fields = ('nombre',)

# Para Especialistas
@admin.register(Especialistas)
class EspecialistasAdmin(admin.ModelAdmin):
    list_display = ('id_especialistas', 'id_especialidad_especialista', 'dni', 'matricula', 'email', 'telefono')
    search_fields = ('dni', 'email')
# ----------------------
# INFORMES
# ----------------------

# ----------------------
# OBSERVACIONES
# ----------------------
@admin.register(Observacion)
class ObservacionAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha', 'tipo_sesion', 'especialista', 'creada_por', 'fecha_registro')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'observacion_clinica', 'especialista')
    list_filter = ('tipo_sesion', 'especialista')

# ----------------------
# TESTIMONIOS
# ----------------------
@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'relacion', 'fecha_envio', 'estado', 'publicado')
    search_fields = ('titulo', 'usuario__username', 'contenido')
    list_filter = ('estado', 'publicado')


