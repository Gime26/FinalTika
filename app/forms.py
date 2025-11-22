from django.forms import ModelForm, NumberInput
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
<<<<<<< HEAD
# 🛑 CORRECCIÓN: Importar el modelo 'Especialista' en singular si la relación de Turno lo usa.
# Si el usuario insiste en 'Especialistas', usaremos el plural. 
# Asumo que el modelo se llama 'Especialista' para consistencia con 'Paciente'.
from .models import Perfil, Entrevista, Paciente, Observacion, Testimonio, Turno, InformeInterdisciplinario, Especialista # Cambiado Especialistas a Especialista
=======
from .models import Perfil, Entrevista, Paciente, EstadisticaPaciente, Observacion, Testimonio, Turno, InformeInterdisciplinario, Especialistas
>>>>>>> a2569c1 (Testimonio index, Estadistica)
from datetime import date
from django.forms.widgets import DateInput, Select, Textarea
from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

class EntrevistaForm(forms.ModelForm):
    """Formulario simple para capturar la solicitud de entrevista."""
    class Meta:
        model = Entrevista 
        fields = '__all__'

class RegisterForm(UserCreationForm):
    """
    Formulario de Registro extendido para crear un Perfil y un Paciente 
    simultáneamente con el objeto User.
    """
    # Campos adicionales para Perfil y Paciente
    dni = forms.IntegerField(label='DNI', required=True) # DNI es clave, requerido
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento', 
        widget=NumberInput(attrs={'type': 'date'}), 
        required=True
    )
    domicilio = forms.CharField(label='Domicilio', max_length=255, required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)

    # 🛑 CORRECCIÓN: Usamos los campos first_name/last_name/email del modelo User, 
    # pero los definimos aquí para hacerlos requeridos/personalizables en el formulario.
    first_name = forms.CharField(label='Nombre', max_length=150, required=True)
    last_name = forms.CharField(label='Apellido', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    
    codigo_terapeuta = forms.CharField(
        label="Código de terapeuta (si corresponde)",
        max_length=50,
        required=False
    )
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            today = date.today()
            age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if age < 18:
                raise forms.ValidationError("Debes ser mayor de 18 años para registrarte.")
        return fecha_nacimiento
    
    class Meta:
        model = User
        fields = (
            'username',
            'first_name', 
            'last_name',
            'email',
            # Campos custom que serán usados en la vista
            'dni',
            'fecha_nacimiento',
            'telefono',
            'domicilio',
            'codigo_terapeuta',
        ) + UserCreationForm.Meta.fields[2:] # Incluir los campos de contraseña

        widgets = {}
        

class LoginForm(forms.Form):
    """Formulario básico de login (no usa AuthenticationForm de Django)."""
    username = forms.CharField(label="Nombre de usuario", max_length=150)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class PacienteForm(forms.ModelForm):
    """Formulario para la gestión de datos del Paciente por el especialista/admin."""
    class Meta:
        model = Paciente
        # 🛑 CORRECCIÓN CLAVE: Cambié 'dni_paciente' por 'dni' para alinearlo con 
        # la lógica de creación de la vista de registro (views.py) y la unicidad del DNI.
        fields = ['dni', 'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'telefono', 'email']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-input'}),
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'apellido': forms.TextInput(attrs={'class': 'form-input'}),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'genero': forms.Select(attrs={'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

class EstadisticaPacienteForm(forms.ModelForm):
    class Meta:
        model = EstadisticaPaciente
        fields = ["nombre", "edad", "especialidad"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "edad": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 18}),
            "especialidad": forms.Select(attrs={"class": "form-control"}),
        }
class ObservacionForm(forms.ModelForm):
    """Formulario para la creación de Observaciones Clínicas."""

    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all().order_by('apellido', 'nombre'),
        empty_label="— Seleccionar —",
        label="Paciente:",
        # 💡 MEJORA: Añadir widget de búsqueda si es posible, pero Select por defecto
    )
    
    # 🛑 CORRECCIÓN: Si 'especialista' es una relación ForeignKey/ModelChoiceField en el modelo Observacion,
    # debe usar un ModelChoiceField, no un ChoiceField con opciones fijas (Observacion.ESPECIALISTAS).
    # Asumo que el campo apunta al modelo Especialista/Especialistas.
    especialista = forms.ModelChoiceField(
        # Asumo que el modelo de Especialistas se llama 'Especialista' (singular).
        queryset=Especialista.objects.all().order_by('nombre'), 
        empty_label="— Seleccionar Especialista —",
        label="Especialista:",
        required=True
    )
    
    # Mantenemos 'tipo_sesion' como ChoiceField si es un campo de elección en el modelo
    tipo_sesion = forms.ChoiceField(
        # Asumo que TIPO_SESION es una tupla de choices definida en el modelo Observacion
        choices=Observacion.TIPO_SESION,
        label="Tipo de sesión:",
        required=True
    )

    class Meta:
        model = Observacion
        fields = ['paciente', 'fecha', 'tipo_sesion', 'especialista', 'observacion_clinica']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'observacion_clinica': forms.Textarea(attrs={'rows': 5})
        }


class TestimonioForm(forms.ModelForm):
    """Formulario para que los usuarios envíen un testimonio."""
    class Meta:
        model = Testimonio
        fields = ['relacion','titulo', 'contenido', 'imagen']
        widgets = {
            'relacion': forms.TextInput(attrs={
                'placeholder': 'Ejemplo: Mamá de Mateo, Papá de Lucía, Tutor de Ana...',
                'class': 'form-control'
            }),
            'contenido': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InformeInterdisciplinarioForm(forms.ModelForm):
    """Formulario para la creación de Informes Interdisciplinarios."""
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    # 🛑 CORRECCIÓN: Uso de ModelMultipleChoiceField correcto, asumiendo Especialista
    especialistas = forms.ModelMultipleChoiceField(
        # Usamos Especialista si corregimos el import, o Especialistas si ese es el nombre del modelo
        queryset=Especialista.objects.all(), 
        widget=forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
        label="Especialistas Participantes"
    )

    class Meta:
        model = InformeInterdisciplinario
        fields = ['fecha', 'asunto', 'especialistas', 'cuerpo']

class PerfilUpdateForm(forms.ModelForm):
    """Formulario para que el usuario (paciente o especialista) actualice su Perfil."""
    class Meta:
        model = Perfil
        fields = [
            'nombre', 'apellido', 'dni', 'nacionalidad',
            'domicilio', 'telefono', 'cp', 'email', 'especialidad', 'matricula'
        ]
        widgets = {
            # Dejar campos clave como read-only es una buena práctica
            'nombre': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            # Campos editables:
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}), # editable para especialistas
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TurnoForm(forms.ModelForm):
    """Formulario para la creación y edición de turnos."""
    
    # 🛑 CORRECCIÓN CLAVE 1: Los nombres de los campos deben ser minúsculas y coincidir con el modelo.
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all().order_by('nombre'),
        label="Paciente",
        empty_label="— Seleccionar Paciente —"
    )
    # 🛑 CORRECCIÓN CLAVE 2: Asumimos 'especialista' singular.
    especialista = forms.ModelChoiceField(
        queryset=Especialista.objects.all().order_by('nombre'),
        label="Especialista",
        empty_label="— Seleccionar Especialista —"
    )
    
    # 🛑 CORRECCIÓN CLAVE 3: Usamos 'date' y 'time' para coincidir con los campos de Meta.
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora"
    )
    
    class Meta:
        model = Turno
        # 🛑 CORRECCIÓN CLAVE 4: Aseguramos que los nombres de los campos coincidan.
        # Asumo que el modelo Turno usa 'especialista' y 'date', 'time'
        fields = ['paciente', 'especialista', 'date', 'time', 'status', 'motivo'] # Agregué status y description (comunes en Turno)
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Uso de los nombres de campo corregidos (date, time)
        turno_date = cleaned_data.get('date')
        turno_time = cleaned_data.get('time')
        
        # Validar que la fecha y hora no estén en el pasado
        if turno_date and turno_time:
            # Combinamos la fecha y hora. 
            try:
                turno_datetime = timezone.datetime.combine(turno_date, turno_time)
            except TypeError:
                # Esto puede ocurrir si alguno de los campos es None después de la limpieza
                raise ValidationError("La fecha y la hora del turno son requeridas.")

            # Comparamos con la hora actual. Usamos timezone.now()
            if turno_datetime < timezone.now():
                # 🛑 CORRECCIÓN: El error debe ser de validación y apuntar al campo
                raise ValidationError({
                    'date': "La fecha y hora no pueden ser anteriores a la hora actual."
                })
        
        # Lógica para la validación de disponibilidad del slot
        # Se debe llamar a full_clean() o clean() del modelo para obtener la validación
        # de slot si no se hace automáticamente. Aquí lo manejamos con una instancia
        try:
            instance = Turno(**cleaned_data)
            
            # Si estamos editando, asignamos el pk para excluir el turno actual
            if self.instance and self.instance.pk:
                instance.pk = self.instance.pk
            
            # Llamamos al método clean del modelo si fuera necesario, aunque un ModelForm
            # lo hace en el save(). Lo mantenemos por si hay una validación manual en el modelo.
            instance.clean_fields(exclude=['status']) # Evitamos errores de status si es None al crear
            
        except ValidationError as e:
            # 🛑 CORRECCIÓN: Si es un error específico de campo, lo propagamos.
            if hasattr(e, 'error_dict') and 'non_field_errors' in e.error_dict:
                 # Si es un error general del modelo (ej: "Slot no disponible")
                raise ValidationError(e.message) 
            # Si es un error de campo, Django lo manejará automáticamente
        
        return cleaned_data