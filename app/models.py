from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class Paciente(models.Model):
    dni_paciente = models.CharField(max_length=20, unique=True, verbose_name="DNI del Paciente")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")

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
    id_entrevista = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo_consulta = models.TextField()
    # Otros campos relevantes

    def __str__(self):
        return f"Entrevista {self.id_entrevista} - Paciente {self.paciente}"

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
    

# 🩺 TURNOS
class Turno(models.Model):
    id_turno = models.IntegerField(db_column='ID_Turno', primary_key=True)
    paciente = models.ForeignKey(Paciente, models.DO_NOTHING, db_column='ID_Paciente')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200)

    def __str__(self):
        return f"Turno {self.id_turno} - Paciente {self.paciente}"
    

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

    def __str__(self):
        return f"Especialista {self.dni or self.id_especialistas}"

class InformeInterdisciplinario(models.Model):
    fecha = models.DateField()
    asunto = models.CharField(max_length=255)
    especialistas = models.ManyToManyField('Especialistas')
    cuerpo = models.TextField(blank=True, null=True)  # campo opcional para contenido del informe

    def __str__(self):
        return f"{self.fecha} - {self.asunto}"

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
    fecha = models.DateField()
    tipo_sesion = models.CharField(max_length=50, choices=TIPO_SESION)
    especialista = models.CharField(max_length=100, choices=ESPECIALISTAS)
    observacion_clinica = models.TextField()
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Obs. de {self.paciente.nombre} el {self.fecha}"


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
    
    