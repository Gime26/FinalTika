from django.db import models
from django.contrib.auth.models import User

class Paciente(models.Model):
    dni_paciente = models.CharField(max_length=20, unique=True, verbose_name="DNI del Paciente")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    
    # Elecciones de Sexo
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    
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
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    numero_documento = models.IntegerField(verbose_name='DNI', null=True, blank=True)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', null=True, blank=True)
    domicilio = models.CharField(verbose_name='Domicilio', max_length=255, blank=True)
    telefono = models.CharField(verbose_name='Teléfono', max_length=20, blank=True)

    def __str__(self):
        return self.user.username


# 🧑 PACIENTE 
class Paciente(models.Model):
    id_paciente = models.IntegerField(db_column='ID_Paciente', primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.IntegerField(db_column='DNI')
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

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