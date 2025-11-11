from django.contrib import admin
from .models import (
    Paciente, Entrevista, Perfil, EstadoPaciente, HistorialPaciente, 
    Turno, Centrosterapeuticos, Detallepagos, Especialidades, Especialistas, 
    Informe, Observacion, Testimonio
)

# ----------------------
# PACIENTES
# ----------------------
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('dni_paciente', 'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'telefono', 'email')
    search_fields = ('nombre', 'apellido', 'dni_paciente', 'email')
    list_filter = ('genero',)

# ----------------------
# ENTREVISTAS
# ----------------------
@admin.register(Entrevista)
class EntrevistaAdmin(admin.ModelAdmin):
    list_display = ('id_entrevista', 'paciente', 'fecha', 'hora', 'motivo_consulta')
    search_fields = ('paciente__nombre', 'paciente__apellido')
    list_filter = ('fecha',)

# ----------------------
# PERFIL USUARIO
# ----------------------
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_documento', 'fecha_nacimiento', 'domicilio', 'telefono')
    search_fields = ('user__username', 'numero_documento')

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
# TURNOS
# ----------------------
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id_turno', 'paciente', 'fecha', 'hora', 'motivo')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'motivo')
    list_filter = ('fecha',)

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

# ----------------------
# ESPECIALIDADES
# ----------------------
@admin.register(Especialidades)
class EspecialidadesAdmin(admin.ModelAdmin):
    list_display = ('id_especialidades', 'id_especialista', 'nombre', 'matricula')
    search_fields = ('nombre',)

# ----------------------
# ESPECIALISTAS
# ----------------------
@admin.register(Especialistas)
class EspecialistasAdmin(admin.ModelAdmin):
    list_display = ('id_especialistas', 'id_especialidad_especialista', 'dni', 'matricula', 'email', 'telefono')
    search_fields = ('dni', 'email')

# ----------------------
# INFORMES
# ----------------------
@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = ('id_informe', 'titulo', 'fecha_creacion')
    search_fields = ('titulo',)
    list_filter = ('fecha_creacion',)

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
