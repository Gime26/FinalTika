from django.contrib import admin
from .models import (
    Entrevista, Especialista, Paciente, Turno,
    Observacion, Testimonio, InformeInterdisciplinario
)

# ====================================================================
# === CLASES ADMIN CORREGIDAS PARA COINCIDIR CON APP/MODELS.PY =======
# ====================================================================

# Se usa 'paciente' y 'especialista' porque son ForeingKeys y Django
# sabe cómo resolverlos automáticamente en list_display.

class EntrevistaAdmin(admin.ModelAdmin):
    # Coincide con: paciente (FK), fecha (DateField), hora (TimeField)
    list_display = ('id', 'paciente', 'fecha', 'hora', 'motivo_consulta')
    # list_display[3] refería a 'especialista', lo cual era incorrecto.
    # El modelo Entrevista NO tiene campo 'especialista' según el models.py, lo corregimos.
    list_filter = ('fecha',)
    search_fields = ('paciente__nombre', 'motivo_consulta')

class EspecialistasAdmin(admin.ModelAdmin):
    # Coincide con: nombre, especialidad. No existe un campo 'apellido'.
    # Error corregido: list_display[2] refería a 'apellido'.
    list_display = ('nombre', 'especialidad', 'matricula', 'dni')
    list_filter = ('especialidad',)
    search_fields = ('nombre', 'especialidad', 'matricula')

class PacienteAdmin(admin.ModelAdmin):
    # Coincide con: dni, nombre, apellido, fecha_nacimiento
    list_display = ('dni', 'nombre', 'apellido', 'genero', 'fecha_nacimiento')
    list_filter = ('genero', 'fecha_nacimiento')
    search_fields = ('dni', 'nombre', 'apellido')

class TurnoAdmin(admin.ModelAdmin):
    # Coincide con: paciente (FK), date (Fecha), time (Hora), status (Estado)
    # Errores corregidos: Usaba 'fecha', 'hora', 'estado'. Corregido a 'date', 'time', 'status'.
    list_display = ('id', 'paciente', 'especialista', 'date', 'time', 'status')
    list_filter = ('date', 'status', 'especialista')
    search_fields = ('paciente__nombre', 'especialista__nombre', 'motivo')

class ObservacionAdmin(admin.ModelAdmin):
    # Coincide con: paciente (FK), especialista (FK), fecha
    list_display = ('paciente', 'fecha', 'tipo_sesion', 'especialista')
    list_filter = ('fecha', 'especialista', 'tipo_sesion')
    search_fields = ('paciente__nombre', 'observacion_clinica')

class TestimonioAdmin(admin.ModelAdmin):
    # Coincide con: usuario (FK), fecha_envio (Fecha), publicado (Aprobado)
    # Errores corregidos: Usaba 'paciente', 'fecha', 'aprobado'. Corregido a 'usuario', 'fecha_envio', 'publicado'.
    list_display = ('usuario', 'titulo', 'fecha_envio', 'publicado', 'estado')
    list_filter = ('publicado', 'estado', 'fecha_envio')
    search_fields = ('usuario__username', 'contenido', 'relacion')

class InformeInterdisciplinarioAdmin(admin.ModelAdmin):
    # Coincide con: fecha, asunto (Título). Los especialistas son ManyToMany (no para list_display directo).
    # Errores corregidos: Usaba 'paciente' (no existe), 'fecha_emision', 'titulo'. Corregido a 'fecha' y 'asunto'.
    list_display = ('id', 'fecha', 'asunto', 'display_especialistas')
    list_filter = ('fecha',)
    search_fields = ('asunto', 'cuerpo')

    # Método para mostrar la lista de especialistas involucrados (solo para list_display)
    def display_especialistas(self, obj):
        return ", ".join([e.nombre for e in obj.especialistas.all()])
    display_especialistas.short_description = 'Especialistas'

# ====================================================================
# === REGISTROS ======================================================
# ====================================================================

admin.site.register(Entrevista, EntrevistaAdmin)
admin.site.register(Especialista, EspecialistasAdmin)
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Turno, TurnoAdmin)
admin.site.register(Observacion, ObservacionAdmin)
admin.site.register(Testimonio, TestimonioAdmin)
admin.site.register(InformeInterdisciplinario, InformeInterdisciplinarioAdmin)