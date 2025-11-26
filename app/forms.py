from django.forms import ModelForm, NumberInput
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from .models import Perfil, Entrevista, Paciente, EstadisticaPaciente, Observacion, Testimonio, Turno, InformeInterdisciplinario, Especialistas, Especialista, SeccionInforme
from datetime import date
from django.forms.widgets import DateInput, Select, Textarea
from django.contrib.auth import get_user_model

User = get_user_model()

class EntrevistaForm(forms.ModelForm):
    class Meta:
        model = Entrevista 
        fields = '__all__'

class RegisterForm(UserCreationForm):
    # Campo DNI único
    dni = forms.CharField(label='DNI', required=True)
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento', 
        widget=NumberInput(attrs={
            'type': 'date',
            'min': '1920-01-01',
            'max': '2010-12-31'
        }), 
        required=True,
        help_text="Fecha entre 1920 y 2010"
    )
    domicilio = forms.CharField(label='Domicilio', max_length=255, required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)

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
            'dni',
            'fecha_nacimiento',
            'telefono',
            'domicilio',
            'codigo_terapeuta',
        ) + UserCreationForm.Meta.fields[2:] 

        widgets = {}

    def clean(self):
        cleaned = super().clean()
        dni_val = cleaned.get('dni')
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
        fields = ['dni', 'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'telefono', 'email']
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'form-input',
                'pattern': '[0-9]{7,8}',
                'inputmode': 'numeric',
                'maxlength': '8',
                'placeholder': '7 u 8 dígitos',
                'title': 'DNI debe tener 7 u 8 dígitos'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'maxlength': '100',
                'placeholder': 'Ingrese el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-input',
                'maxlength': '100',
                'placeholder': 'Ingrese el apellido'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'min': '1920-01-01',
                'max': '2024-12-31'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-input'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-input',
                'pattern': '[0-9]{10}',
                'inputmode': 'numeric',
                'maxlength': '10',
                'placeholder': '10 dígitos sin guiones',
                'title': 'Teléfono debe tener 10 dígitos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'ejemplo@email.com'
            }),
        }
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni:
            raise forms.ValidationError("El DNI es obligatorio.")
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if len(dni) < 7 or len(dni) > 8:
            raise forms.ValidationError("El DNI debe tener 7 u 8 dígitos.")
        
        # Verificar que no exista otro paciente con el mismo DNI
        qs = Paciente.objects.filter(dni=dni)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un paciente con ese DNI.")
        return dni
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError("El nombre solo debe contener letras.")
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre.strip()
    
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio.")
        if not apellido.replace(' ', '').isalpha():
            raise forms.ValidationError("El apellido solo debe contener letras.")
        if len(apellido) < 2:
            raise forms.ValidationError("El apellido debe tener al menos 2 caracteres.")
        return apellido.strip()
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono debe contener solo números.")
            if len(telefono) != 10:
                raise forms.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
        return telefono
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.lower().strip()
        return email
    
    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha:
            from datetime import date
            today = date.today()
            age = today.year - fecha.year - ((today.month, today.day) < (fecha.month, fecha.day))
            if age > 100:
                raise forms.ValidationError("La fecha de nacimiento no es válida.")
            if fecha > today:
                raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha

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
        label="Especialista:",
        disabled=True,  # No editable
        required=False
    )

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha:
            if fecha.year < 2020 or fecha.year > 2030:
                raise forms.ValidationError('La fecha debe estar entre 2020 y 2030')
        return fecha

    class Meta:
        model = Observacion
        fields = ['paciente', 'fecha', 'tipo_sesion', 'especialista', 'observacion_clinica']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'min': '2020-01-01',
                'max': '2030-12-31'
            }),
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

class TurnoFormGestion(forms.ModelForm):
    """Formulario para gestión completa de turnos con especialista y estado"""
    class Meta:
        model = Turno
        fields = ['paciente', 'especialista', 'fecha', 'hora', 'motivo', 'status']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'especialista': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        especialista = cleaned_data.get('especialista')
        status = cleaned_data.get('status')
        
        if fecha and hora:
            from datetime import datetime
            turno_datetime = datetime.combine(fecha, hora)
            if turno_datetime < datetime.now():
                raise forms.ValidationError("No se puede agendar un turno en el pasado.")
        
        # Validar disponibilidad solo si el estado es PENDING o CONFIRMED
        if status in ['PENDING', 'CONFIRMED'] and fecha and hora and especialista:
            conflicting = Turno.objects.filter(
                especialista=especialista,
                fecha=fecha,
                hora=hora
            ).exclude(status__in=['CANCELLED', 'COMPLETED'])
            
            if self.instance.pk:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            
            if conflicting.exists():
                raise forms.ValidationError(
                    f"El especialista {especialista.nombre} ya tiene un turno en esta fecha y hora."
                )
        
        return cleaned_data


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
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        empty_label="— Seleccionar paciente —",
        label="Paciente",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_informe = forms.DateField(
        label="Fecha del informe",
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'min': '2020-01-01',
            'max': '2030-12-31'
        }),
        help_text="Fecha entre 2020 y 2030"
    )
    
    asunto = forms.CharField(
        label="Asunto del informe",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Evaluación trimestral'})
    )
    
    especialistas = forms.ModelMultipleChoiceField(
        queryset=Perfil.objects.filter(rol='especialista'),
        label="Especialistas colaboradores",
        widget=forms.CheckboxSelectMultiple(),
        help_text="Selecciona los especialistas que trabajarán en este informe"
    )
    
    descripcion_general = forms.CharField(
        label="Descripción general (opcional)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción general del caso...'})
    )

    def clean_fecha_informe(self):
        fecha = self.cleaned_data.get('fecha_informe')
        if fecha:
            if fecha.year < 2020 or fecha.year > 2030:
                raise forms.ValidationError('La fecha debe estar entre 2020 y 2030')
        return fecha

    class Meta:
        model = InformeInterdisciplinario
        fields = ['paciente', 'fecha_informe', 'asunto', 'especialistas', 'descripcion_general']


class SeccionInformeForm(forms.ModelForm):
    """Formulario para que cada especialista agregue su sección"""
    contenido = forms.CharField(
        label="Tu aporte al informe",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Escribe tu evaluación, observaciones y recomendaciones...'})
    )
    
    class Meta:
        model = SeccionInforme
        fields = ['contenido']

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'nombre', 'apellido', 'dni', 'nacionalidad',
            'domicilio', 'telefono', 'cp', 'email', 'especialidad', 'matricula'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'maxlength': '100',
                'placeholder': 'Ingrese su nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control', 
                'maxlength': '100',
                'placeholder': 'Ingrese su apellido'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control', 
                'pattern': '[0-9]{7,8}', 
                'inputmode': 'numeric',
                'maxlength': '8',
                'placeholder': '7 u 8 dígitos',
                'title': 'DNI debe tener 7 u 8 dígitos'
            }),
            'nacionalidad': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '50',
                'placeholder': 'Ejemplo: Argentina'
            }),
            'domicilio': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Calle y número'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 
                'pattern': '[0-9]{10}', 
                'inputmode': 'numeric',
                'maxlength': '10',
                'placeholder': '10 dígitos sin guiones',
                'title': 'Teléfono debe tener 10 dígitos'
            }),
            'cp': forms.TextInput(attrs={
                'class': 'form-control', 
                'pattern': '[0-9]{4}', 
                'inputmode': 'numeric',
                'maxlength': '4',
                'placeholder': '4 dígitos',
                'title': 'Código postal debe tener 4 dígitos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@email.com'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '80',
                'placeholder': 'Ejemplo: Psicología'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control', 
                'pattern': '[0-9]{1,10}', 
                'inputmode': 'numeric',
                'maxlength': '10',
                'placeholder': 'Solo números',
                'title': 'Matrícula debe contener solo números'
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError("El nombre solo debe contener letras.")
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre.strip()
    
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio.")
        if not apellido.replace(' ', '').isalpha():
            raise forms.ValidationError("El apellido solo debe contener letras.")
        if len(apellido) < 2:
            raise forms.ValidationError("El apellido debe tener al menos 2 caracteres.")
        return apellido.strip()
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono:
            return telefono
        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono debe contener solo números.")
        if len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
        return telefono
    
    def clean_cp(self):
        cp = self.cleaned_data.get('cp')
        if not cp:
            return cp
        if not cp.isdigit():
            raise forms.ValidationError("El código postal debe contener solo números.")
        if len(cp) != 4:
            raise forms.ValidationError("El código postal debe tener exactamente 4 dígitos.")
        return cp
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if not matricula:
            return matricula
        if not matricula.isdigit():
            raise forms.ValidationError("La matrícula debe contener solo números.")
        if len(matricula) < 1 or len(matricula) > 10:
            raise forms.ValidationError("La matrícula debe tener entre 1 y 10 dígitos.")
        return matricula

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni:
            raise forms.ValidationError("El DNI es obligatorio.")
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if len(dni) < 7 or len(dni) > 8:
            raise forms.ValidationError("El DNI debe tener 7 u 8 dígitos.")
        
        # Verificar que no exista otro perfil con el mismo DNI
        qs = Perfil.objects.filter(dni=dni)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con ese DNI.")
        return dni
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("El email es obligatorio.")
        return email.lower().strip()