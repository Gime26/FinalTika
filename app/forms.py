# app/forms.py (¡Versión Final y Correcta!)

from django.forms import ModelForm, NumberInput
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from .models import Perfil, Entrevista, Paciente, Especialidades, Observacion, Testimonio, Turno
from datetime import date
from django.forms.widgets import DateInput, Select, Textarea

class EntrevistaForm(forms.ModelForm):
    class Meta:
        # Asegúrate de que 'Entrevista' sea el nombre correcto de tu modelo.
        model = Entrevista 
        fields = '__all__' # O la lista específica de campos que necesites

class RegisterForm(UserCreationForm):
    # ✅ CAMPOS DE PERFIL DEFINIDOS AQUÍ (NO en Meta)
    # Deben estar fuera para que Django no intente mapearlos al modelo User.
    numero_documento = forms.IntegerField(label='DNI', required=False)
    fecha_nacimiento = forms.DateField(label='Fecha de Nacimiento', 
                                       widget=NumberInput(attrs={'type': 'date'}), 
                                       required=False)
    domicilio = forms.CharField(label='Domicilio', max_length=255, required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    
    # ✅ CAMPOS ADICIONALES DE USER DEFINIDOS AQUÍ
    first_name = forms.CharField(label='Nombre', max_length=150, required=False)
    last_name = forms.CharField(label='Apellido', max_length=150, required=False)
    email = forms.EmailField(label='Email', required=False)

    def clean_fecha_nacimiento(self):
        # ... (Tu lógica de validación de edad) ...
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            today = date.today()
            age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if age < 18:
                raise forms.ValidationError("Debes ser mayor de 18 años para registrarte.")
        return fecha_nacimiento
    
    class Meta:
        model = User
        # 🟢 CORRECCIÓN CLAVE: ¡SOLO CAMPOS DE MODELO USER AQUÍ!
        fields = (
            'username',
            'first_name', 
            'last_name',
            'email',
        ) + UserCreationForm.Meta.fields[2:] # Esto mantiene los campos de password.

        # 🟢 Eliminamos los widgets que referencian campos de Perfil.
        widgets = {}

class LoginForm(forms.Form):
    # Asegúrate de que los nombres sean 'username' y 'password'
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
