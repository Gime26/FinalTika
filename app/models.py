from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class Paciente(models.Model):
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI del Paciente", db_column='dni')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)

    # Elecciones de Sexo
    GENERO_CHOICES = [
      ('M', 'Masculino'),
      ('F', 'Femenino'),
      ('O', 'Otro'),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

 #ESTO ACABO DE AUMENTAR DE 28/11
class Entrevista(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Revisión'),
        ('en_revision', 'En Revisión'),
        ('derivada', 'Derivada'),
        ('contactada', 'Contactada'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo_consulta = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    especialista_asignado = models.ForeignKey('Especialista', on_delete=models.SET_NULL, null=True, blank=True, related_name='entrevistas_asignadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    observaciones = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Entrevista {self.id} - Paciente {self.paciente}"

# 👤 PERFIL DE USUARIO
# models.py
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, default="", blank=True)
    apellido = models.CharField(max_length=100, default="Desconocido", blank=True)
    dni = models.CharField(max_length=20, default="", blank=True, unique=True)
    nacionalidad = models.CharField(max_length=50, default="", blank=True)
    domicilio = models.CharField(max_length=100, default="", blank=True)
    telefono = models.CharField(max_length=20, default="", blank=True)
    cp = models.CharField(max_length=10, default="", blank=True)
    email = models.EmailField(default="", blank=True)

    especialidad = models.CharField(max_length=80, default="", blank=True)
    matricula = models.CharField(max_length=20, default="", blank=True)

    rol = models.CharField(
        max_length=20,
        choices=[('paciente', 'Paciente'), ('especialista', 'Especialista')],
        default='paciente'
    )

    # 👉 Relación con Paciente
    paciente = models.OneToOneField(
        'Paciente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.rol}"


# 📊 ESTADO DEL PACIENTE
class EstadoPaciente(models.Model):
    id_estado = models.IntegerField(primary_key=True)
    nombre_estado = models.CharField(max_length=50)
    # ... otros campos
    
    class Meta:
        managed = False
        # db_table = 'estadopaciente' 
        
    def __str__(self):
        return self.nombre_estado
    
# 🩺 HISTORIAL PACIENTE
class HistorialPaciente(models.Model):
    nro_historia_paciente = models.IntegerField(db_column='Nro_Historia_paciente', primary_key=True)
    antecedentes = models.CharField(db_column='Antecedentes', max_length=200, blank=True, null=True)
    observaciones = models.CharField(verbose_name="Observaciones", max_length=50, blank=True, null=True)
    paciente = models.ForeignKey(Paciente, models.DO_NOTHING, db_column='ID_Paciente')
    estado_paciente = models.ForeignKey(EstadoPaciente, models.DO_NOTHING, db_column='ID_Estado')
    # ... otros campos
    class Meta:
        managed = False
        # db_table = 'historialpaciente'
    def __str__(self):
        return f"Historial de {self.paciente.nombre} {self.paciente.apellido}"
    

# 🩺 TURNOS Y ESPECIALISTAS
STATUS_CHOICES = [
    ('PENDING', 'Pendiente'),
    ('CONFIRMED', 'Confirmado'),
    ('CANCELLED', 'Cancelado'),
    ('COMPLETED', 'Completado'),
]

class Especialista(models.Model):
    """Modelo para especialistas/profesionales"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad")
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula", null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    perfil = models.OneToOneField(Perfil, on_delete=models.SET_NULL, null=True, blank=True, related_name='especialista_relacionado', verbose_name="Perfil de usuario")
    
    class Meta:
        verbose_name = "Especialista"
        verbose_name_plural = "Especialistas"
    
    def __str__(self):
        return f"{self.nombre} - {self.especialidad}"

class Turno(models.Model):
    """Modelo de turno con validación y estados"""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, verbose_name="Especialista", null=True, blank=True)
    fecha = models.DateField(verbose_name="Fecha", db_column='date')
    hora = models.TimeField(verbose_name="Hora", db_column='time')
    motivo = models.CharField(max_length=200, verbose_name="Motivo", blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Estado"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='turnos_creados', verbose_name="Creado por")
    
    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        unique_together = ('especialista', 'fecha', 'hora')
        ordering = ['fecha', 'hora']
    
    def __str__(self):
        return f"Turno de {self.paciente.nombre} con {self.especialista.nombre} - {self.fecha} {self.hora}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        import datetime
        
        # Validar que no sea fecha/hora pasada
        turno_datetime = datetime.datetime.combine(self.fecha, self.hora)
        if turno_datetime < datetime.datetime.now():
            raise ValidationError("No se puede agendar un turno en el pasado.")
        
        # Validar disponibilidad (solo para turnos pendientes o confirmados)
        if self.status in ['PENDING', 'CONFIRMED']:
            conflicting = Turno.objects.filter(
                especialista=self.especialista,
                fecha=self.fecha,
                hora=self.hora
            ).exclude(status__in=['CANCELLED', 'COMPLETED'])
            
            if self.pk:
                conflicting = conflicting.exclude(pk=self.pk)
            
            if conflicting.exists():
                raise ValidationError(f"El especialista {self.especialista.nombre} ya tiene un turno en esta fecha y hora.")
    

# 🏥 CENTROS TERAPÉUTICOS
class Centrosterapeuticos(models.Model):
    id_centroterapeutico = models.IntegerField(db_column='ID_CentroTerapeutico', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)
    telefono = models.IntegerField(db_column='Telefono', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'centrosterapeuticos'

    def __str__(self):
        return self.nombre or f"Centro {self.id_centroterapeutico}"


# 💳 DETALLE DE PAGOS
class Detallepagos(models.Model):
    codigo_pago = models.IntegerField(db_column='Codigo_Pago', primary_key=True)
    monto = models.DecimalField(db_column='Monto', max_digits=10, decimal_places=2, blank=True, null=True)
    observaciones = models.CharField(db_column='Observaciones', max_length=400, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detallepagos'

    def __str__(self):
        return f"Pago {self.codigo_pago} - ${self.monto}"


# 🧠 ESPECIALIDADES
class Especialidades(models.Model):
    id_especialidades = models.IntegerField(db_column='id_Especialidades', primary_key=True)
    id_especialista = models.IntegerField()
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)
    matricula = models.IntegerField(db_column='Matricula', blank=True, null=True)

    class Meta:
        db_table = 'especialidades'
        managed = False

    def __str__(self):
        return self.nombre or f"Especialidad {self.id_especialidades}"


# 👩‍⚕️ ESPECIALISTAS
class Especialistas(models.Model):
    id_especialistas = models.IntegerField(db_column='ID_Especialistas', primary_key=True)
    id_especialidad_especialista = models.CharField(max_length=45, blank=True, null=True)
    dni = models.IntegerField(db_column='DNI', blank=True, null=True)
    matricula = models.IntegerField(db_column='Matricula', blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    telefono = models.IntegerField(db_column='Telefono', blank=True, null=True)

    class Meta:
        db_table = 'especialistas'
        managed = False

    def __str__(self):
        return f"Especialista {self.dni or self.id_especialistas}"

class InformeInterdisciplinario(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='informes', null=True, blank=True)
    asunto = models.CharField(max_length=255, verbose_name="Asunto del informe", default="Sin asunto")
    fecha_informe = models.DateField(verbose_name="Fecha del informe", null=True, blank=True)
    
    # Especialistas que colaboran en este informe
    especialistas = models.ManyToManyField(Perfil, limit_choices_to={'rol': 'especialista'}, related_name='informes_colaborados')
    
    # Contenido general del informe
    descripcion_general = models.TextField(blank=True, null=True, verbose_name="Descripción general")
    
    # Metadata
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='informes_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Creado el")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        ordering = ['-fecha_informe']
        verbose_name = "Informe Interdisciplinario"
        verbose_name_plural = "Informes Interdisciplinarios"

    def __str__(self):
        fecha_creacion_str = self.fecha_creacion.strftime('%d/%m/%Y') if self.fecha_creacion else 'N/A'
        return f"Informe del {self.fecha_informe.strftime('%d/%m/%Y')} - {self.paciente.nombre} {self.paciente.apellido} - {self.asunto} (creado el {fecha_creacion_str})"


class SeccionInforme(models.Model):
    """Sección del informe completada por cada especialista"""
    informe = models.ForeignKey(InformeInterdisciplinario, on_delete=models.CASCADE, related_name='secciones')
    especialista = models.ForeignKey(Perfil, on_delete=models.CASCADE, limit_choices_to={'rol': 'especialista'})
    contenido = models.TextField(verbose_name="Contenido de la sección")
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Creado el")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = "Sección de Informe"
        verbose_name_plural = "Secciones de Informe"
        unique_together = ['informe', 'especialista']  # Cada especialista tiene una sección por informe

    def __str__(self):
        return f"{self.informe.asunto} - {self.especialista.nombre} {self.especialista.apellido}"

class EstadisticaPaciente(models.Model):
    ESPECIALIDADES = [
        ("Psicología", "Psicología"),
        ("Fonoaudiología", "Fonoaudiología"),
        ("Kinesiología", "Kinesiología"),
        ("Psicomotricidad", "Psicomotricidad"),
        ("Psicopedagogía", "Psicopedagogía"),
    ]

    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    especialidad = models.CharField(max_length=50, choices=ESPECIALIDADES)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.especialidad})"

class Observacion(models.Model):

    ESPECIALISTAS = [
        ("sol_psico", "Lic. Sol Espasandin"),
        ("carlos_kine", "Lic. Carlos Herrera"),
        ("mailen_psico", "Lic. Mailen Danilowicz"),
        ("silvina_psico", "Lic. Silvina Diaz"),
        ("carolina_psicope", "Lic. Carolina Herrera"),
        ("monica_fono", "Lic. Monica Palacios Cañizares"),
        ("itati_psicope", "Lic. Itati Gordillo"),
    ]

    TIPO_SESION = [
        ("psicologia", "Psicología"),
        ("psicopedagogia", "Psicopedagogía"),
        ("psicomotricidad", "Psicomotricidad"),
        ("fonoaudiologia", "Fonoaudiología"),
        ("kinesiologia", "Kinesiología"),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(verbose_name="Fecha y hora de la sesión")
    tipo_sesion = models.CharField(max_length=50, choices=TIPO_SESION)
    especialista = models.CharField(max_length=100, choices=ESPECIALISTAS)
    observacion_clinica = models.TextField()
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Obs. de {self.paciente.nombre} el {self.fecha.strftime('%d/%m/%Y %H:%M')}"


class Testimonio(models.Model):
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

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    