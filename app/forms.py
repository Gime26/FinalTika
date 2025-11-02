# app/forms.py (¡Versión Final y Correcta!)

from django.forms import ModelForm, NumberInput
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from .models import Perfil, Entrevista, Paciente, Informe  
from datetime import date


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


# ✅ Formulario de Login Estándar (Mantener solo este)
class LoginForm(AuthenticationForm):
    pass


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dni_paciente', 'nombre', 'apellido', 'fecha_nacimiento', 'sexo', 'telefono', 'email']

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['titulo', 'contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 4}),
        }

