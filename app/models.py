from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

# Obtener el modelo de usuario activo (necesario para Perfil y Observacion)
User = get_user_model()

# ====================================================================
# === 1. MODELOS BASE PARA AGENDAMIENTO Y PERSONAS (UNIFICADOS) ======
# ====================================================================

# Opciones de estado para el Turno
STATUS_CHOICES = [
    ('PENDING', 'Pendiente'),
    ('CONFIRMED', 'Confirmado'),
    ('CANCELLED', 'Cancelado'),
    ('COMPLETED', 'Completado'),
]

class Paciente(models.Model):
    """
    Representa a un paciente. Único modelo de Paciente,
    incluye todos los campos de información detallada.
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido", default="")
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    
    GENERO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, default='O')
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        
    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"

class Especialista(models.Model):
    """
    Representa a un profesional o terapeuta (único modelo).
    Incluye campos de agendamiento y de la DB externa/legacy unificados.
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad")
    
    # Campos Unificados de la antigua EspecialistasDB
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI", blank=True, null=True)
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    telefono = models.CharField(max_length=20, verbose_name="Teléfono", blank=True, null=True)
    
    class Meta:
        verbose_name = "Especialista"
        verbose_name_plural = "Especialistas"
        
    def __str__(self):
        return f"Lic. {self.nombre} ({self.especialidad})"

class Turno(models.Model):
    """Representa un turno asignado con validación de slot."""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, verbose_name="Especialista")
    date = models.DateField(verbose_name="Fecha")
    time = models.TimeField(verbose_name="Hora")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Estado"
    )
    motivo = models.CharField(max_length=200, verbose_name="Motivo del Turno", default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        # Restricción: un profesional no puede tener dos turnos activos a la misma hora y fecha.
        unique_together = ('especialista', 'date', 'time')
        ordering = ['date', 'time']

    def __str__(self):
        return f"Turno de {self.paciente.nombre} con {self.especialista.nombre} el {self.date} a las {self.time}"
    
    def clean(self):
        # 1. Validación: La fecha y hora no deben ser pasadas
        turno_datetime = timezone.datetime.combine(self.date, self.time)
        if turno_datetime < timezone.now():
            raise ValidationError("No se puede agendar un turno en el pasado.")

        # 2. Validación de disponibilidad para turnos nuevos o modificados
        if self.status in ['PENDING', 'CONFIRMED']:
            
            conflicting_turnos = Turno.objects.filter(
                especialista=self.especialista,
                date=self.date,
                time=self.time
            ).exclude(status__in=['CANCELLED', 'COMPLETED']) 

            if self.pk:
                conflicting_turnos = conflicting_turnos.exclude(pk=self.pk)

            if conflicting_turnos.exists():
                raise ValidationError(f"El Lic. {self.especialista.nombre} ya tiene un turno asignado y activo en esta fecha y hora.")


# ====================================================================
# === 2. MODELOS RELACIONADOS Y TABLAS EXTERNAS/LEGACY (AJUSTADOS) ===
# ====================================================================

# 👤 PERFIL DE USUARIO
class Perfil(models.Model):
    """Perfil de usuario asociado al sistema de autenticación de Django."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, default="", blank=True)
    apellido = models.CharField(max_length=100, default="Desconocido", blank=True)
    dni = models.CharField(max_length=11, default="SinDNI", blank=True)
    nacionalidad = models.CharField(max_length=50, default="", blank=True)
    domicilio = models.CharField(max_length=100, default="", blank=True)
    telefono = models.CharField(max_length=20, default="", blank=True)
    cp = models.CharField(max_length=10, default="", blank=True)
    email = models.EmailField(default="", blank=True)

    # Campos de especialista (ahora pueden ser redundantes con la FK de abajo, pero se mantienen si el Perfil *es* un especialista)
    especialidad = models.CharField(max_length=80, default="", blank=True)
    matricula = models.CharField(max_length=20, default="", blank=True)

    rol = models.CharField(
        max_length=20,
        choices=[('paciente', 'Paciente'), ('especialista', 'Especialista')],
        default='paciente'
    )

    # 👉 Relación con el modelo Paciente principal
    paciente = models.OneToOneField(
        Paciente, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # 👉 Relación con el modelo Especialista principal
    especialista_rel = models.OneToOneField(
        Especialista, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Especialista asociado"
    )

    def __str__(self):
        return f"{self.user.username} - {self.rol}"


# Entrevista (Asociada al modelo Paciente principal)
class Entrevista(models.Model):
    """Información de la entrevista inicial del paciente."""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    fecha = models.DateField()
    hora = models.TimeField()
    motivo_consulta = models.TextField(verbose_name="Motivo de la Consulta")
    
    class Meta:
        verbose_name = "Entrevista"
        verbose_name_plural = "Entrevistas"

    def __str__(self):
        return f"Entrevista de {self.paciente} el {self.fecha}"


# 📊 ESTADO DEL PACIENTE (Tabla Externa/Legacy)
class EstadoPaciente(models.Model):
    """Estado del paciente (posiblemente de una tabla externa)."""
    id_estado = models.IntegerField(primary_key=True)
    nombre_estado = models.CharField(max_length=50)
    
    class Meta:
        managed = False # Indica que Django no gestionará esta tabla
        verbose_name = "Estado del Paciente"
        verbose_name_plural = "Estados del Paciente"
        
    def __str__(self):
        return self.nombre_estado
    
# 🩺 HISTORIAL PACIENTE (Tabla Externa/Legacy)
class HistorialPaciente(models.Model):
    """Historial del paciente (posiblemente de una tabla externa)."""
    nro_historia_paciente = models.IntegerField(db_column='Nro_Historia_paciente', primary_key=True)
    antecedentes = models.CharField(db_column='Antecedentes', max_length=200, blank=True, null=True)
    observaciones = models.CharField(verbose_name="Observaciones", max_length=50, blank=True, null=True)
    # Apunta al modelo Paciente principal
    paciente = models.ForeignKey(Paciente, models.DO_NOTHING, db_column='ID_Paciente') 
    estado_paciente = models.ForeignKey(EstadoPaciente, models.DO_NOTHING, db_column='ID_Estado')
    
    class Meta:
        managed = False
        verbose_name = "Historial del Paciente"
        verbose_name_plural = "Historiales de Pacientes"

    def __str__(self):
        return f"Historial de {self.paciente.nombre} {self.paciente.apellido}"
    

# 🏥 CENTROS TERAPÉUTICOS (Tabla Externa/Legacy)
class Centrosterapeuticos(models.Model):
    """Centros Terapéuticos (posiblemente de una tabla externa)."""
    id_centroterapeutico = models.IntegerField(db_column='ID_CentroTerapeutico', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)
    telefono = models.IntegerField(db_column='Telefono', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'centrosterapeuticos'
        verbose_name = "Centro Terapéutico"
        verbose_name_plural = "Centros Terapéuticos"

    def __str__(self):
        return self.nombre or f"Centro {self.id_centroterapeutico}"


# 💳 DETALLE DE PAGOS (Tabla Externa/Legacy)
class Detallepagos(models.Model):
    """Detalle de Pagos (posiblemente de una tabla externa)."""
    codigo_pago = models.IntegerField(db_column='Codigo_Pago', primary_key=True)
    monto = models.DecimalField(db_column='Monto', max_digits=10, decimal_places=2, blank=True, null=True)
    observaciones = models.CharField(db_column='Observaciones', max_length=400, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detallepagos'
        verbose_name = "Detalle de Pago"
        verbose_name_plural = "Detalles de Pago"

    def __str__(self):
        return f"Pago {self.codigo_pago} - ${self.monto}"


# 🧠 ESPECIALIDADES (Tabla Externa/Legacy - Usada como catálogo)
class Especialidades(models.Model):
    """Tipos de Especialidades (posiblemente de una tabla externa/catálogo)."""
    id_especialidades = models.IntegerField(db_column='id_Especialidades', primary_key=True)
    id_especialista = models.IntegerField(blank=True, null=True) # Este campo es un ID de especialista que ya no necesitamos
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)
    matricula = models.IntegerField(db_column='Matricula', blank=True, null=True)

    class Meta:
        # Si esta es una tabla de *catalogo* y no de la DB externa, la dejamos gestionada.
        # Si es externa, debería ser managed=False. Lo dejo gestionado por ahora, como estaba.
        db_table = 'especialidades' 
        verbose_name = "Especialidad (Catálogo)"
        verbose_name_plural = "Especialidades (Catálogo)"

    def __str__(self):
        return self.nombre or f"Especialidad {self.id_especialidades}"


# Informe Interdisciplinario (Ahora apunta al modelo Especialista unificado)
class InformeInterdisciplinario(models.Model):
    """Informe que puede involucrar a varios especialistas."""
    fecha = models.DateField()
    asunto = models.CharField(max_length=255)
    # 👉 Usamos el modelo Especialista unificado para el ManyToMany
    especialistas = models.ManyToManyField(Especialista, verbose_name="Especialistas Involucrados") 
    cuerpo = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Informe Interdisciplinario"
        verbose_name_plural = "Informes Interdisciplinarios"

    def __str__(self):
        return f"{self.fecha} - {self.asunto}"

    
class Observacion(models.Model):
    """Registro de observación clínica de una sesión."""

    TIPO_SESION = [
        ("psicologia", "Psicología"),
        ("psicopedagogia", "Psicopedagogía"),
        ("psicomotricidad", "Psicomotricidad"),
        ("fonoaudiologia", "Fonoaudiología"),
        ("kinesiologia", "Kinesiología"),
    ]

    # Apunta al modelo Paciente principal
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente") 
    fecha = models.DateField()
    tipo_sesion = models.CharField(max_length=50, choices=TIPO_SESION)
    
    # 👉 Usamos una FK al modelo Especialista unificado en lugar de la lista estática
    especialista = models.ForeignKey(Especialista, on_delete=models.PROTECT, verbose_name="Especialista")
    
    observacion_clinica = models.TextField(verbose_name="Observación Clínica")
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creada Por")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Observación de Sesión"
        verbose_name_plural = "Observaciones de Sesiones"

    def __str__(self):
        return f"Obs. de {self.paciente.nombre} el {self.fecha}"


class Testimonio(models.Model):
    """Testimonios de usuarios o familiares."""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Publicado'),
        ('restringido', 'Restringido'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonios')
    titulo = models.CharField(max_length=100, verbose_name="Título del testimonio")
    relacion = models.CharField(max_length=100, verbose_name="Tu relación con el niño/a (ejemplo: Mamá de Mateo, Tutor de Ana)")
    contenido = models.TextField(verbose_name="Contenido")
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    publicado = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='testimonios/', blank=True, null=True)

    class Meta:
        verbose_name = "Testimonio"
        verbose_name_plural = "Testimonios"

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"