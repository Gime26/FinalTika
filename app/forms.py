from django.forms import ModelForm, NumberInput
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from .models import Perfil, Entrevista, Paciente, EstadisticaPaciente, Observacion, Testimonio, Turno, InformeInterdisciplinario, Especialistas
from datetime import date
from django.forms.widgets import DateInput, Select, Textarea
from django.contrib.auth import get_user_model

User = get_user_model()

class EntrevistaForm(forms.ModelForm):
    class Meta:
        model = Entrevista 
        fields = '__all__'

class RegisterForm(UserCreationForm):
    # Usamos campo de texto para permitir ceros a la izquierda y variantes
    numero_documento = forms.CharField(label='DNI', required=False)
    # Alias 'dni' para compatibilidad con vistas que esperan 'dni'
    dni = forms.CharField(label='DNI', required=False)
    fecha_nacimiento = forms.DateField(label='Fecha de Nacimiento', 
                                       widget=NumberInput(attrs={'type': 'date'}), 
                                       required=False)
    domicilio = forms.CharField(label='Domicilio', max_length=255, required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)

    first_name = forms.CharField(label='Nombre', max_length=150, required=False)
    last_name = forms.CharField(label='Apellido', max_length=150, required=False)
    email = forms.EmailField(label='Email', required=False)

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
        ) + UserCreationForm.Meta.fields[2:] 

        widgets = {}
        
    codigo_terapeuta = forms.CharField(
    label="Código de terapeuta (si corresponde)",
    max_length=50,
    required=False
)

    def clean(self):
        cleaned = super().clean()
        dni_val = cleaned.get('dni') or cleaned.get('numero_documento')
        if dni_val:
            # Normalizar a str
            dni_str = str(dni_val).strip()
            if Perfil.objects.filter(dni=dni_str).exists():
                self.add_error('dni', 'Ya existe un usuario con ese DNI.')
        return cleaned

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario", max_length=150)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    # (Debe tener la lógica para limpiar y autenticar si no usas AuthenticationForm de Django)


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dni_paciente', 'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'telefono', 'email']
        widgets = {
            'dni_paciente': forms.TextInput(attrs={'class': 'form-input'}),
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

    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        empty_label="— Seleccionar —",
        label="Paciente:"
    )

    tipo_sesion = forms.ChoiceField(
        choices=Observacion.TIPO_SESION,
        label="Tipo de sesión:"
    )

    especialista = forms.ChoiceField(
        choices=Observacion.ESPECIALISTAS,
        label="Especialista:"
    )

    class Meta:
        model = Observacion
        fields = ['paciente', 'fecha', 'tipo_sesion', 'especialista', 'observacion_clinica']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'observacion_clinica': forms.Textarea(attrs={'rows': 5})
        }

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['paciente', 'fecha', 'hora', 'motivo']
        
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }

class TestimonioForm(forms.ModelForm):
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
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    especialistas = forms.ModelMultipleChoiceField(
        queryset=Especialistas.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-multiselect'})
    )

    class Meta:
        model = InformeInterdisciplinario
        fields = ['fecha', 'asunto', 'especialistas', 'cuerpo']

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'nombre', 'apellido', 'dni', 'nacionalidad',
            'domicilio', 'telefono', 'cp', 'email', 'especialidad', 'matricula'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
        }

        def clean_dni(self):
            dni = self.cleaned_data.get('dni')
            if not dni:
                return dni
            qs = Perfil.objects.filter(dni=dni)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un usuario con ese DNI.")
            return dni