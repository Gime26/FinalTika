from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
# Importar todas las clases de formularios desde forms.py
from .forms import LoginForm, RegisterForm, EntrevistaForm, PacienteForm
from .models import Perfil , Paciente


# La vista principal que renderiza index.html y pasa ambos formularios para los modales
def inicio(request):
    # Instanciar ambos formularios para los modales en index.html
    login_form = LoginForm()
    entrevista_form = EntrevistaForm() 
    
    # Usamos nombres específicos en el contexto para evitar conflictos
    context = {
        'login_form': login_form, 
        'entrevista_form': entrevista_form,
    }
    
    return render(request, 'index.html', context)


# Vista para mostrar el modal/login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Intentamos autenticar usando el campo 'username' (que puede ser nombre de usuario o email si lo configuraste así)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # NOTA: Si Django solo autentica por username, 
            # podrías necesitar una lógica extra para buscar por email aquí.
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido {user.username}!")
                return redirect('dashboard')  # 👉 Cambia 'dashboard' por tu vista de destino
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    # Si se accede directamente a /login/ o si el POST falla, 
    # se renderiza la plantilla de login dedicada.
    return render(request, 'login.html', {'form': form})


# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('inicio')  # redirige al inicio


# Vista para procesar la Entrevista desde el modal en index.html
def entrevista_view(request):
    if request.method == 'POST':
        form = EntrevistaForm(request.POST)
        if form.is_valid():
            # Guarda la entrevista en la base de datos (asumiendo que EntrevistaForm es un ModelForm)
            form.save()
            messages.success(request, "Entrevista enviada correctamente. Pronto nos pondremos en contacto.")
            return redirect('inicio') # Redirige a inicio después del éxito (cambia 'gracias' por la URL que uses)
        else:
            # Si la validación falla, volvemos a renderizar index.html con los errores
            # También debemos pasar el LoginForm para que el otro modal no se rompa
            login_form = LoginForm() 
            context = {
                'entrevista_form': form, # El formulario con errores
                'login_form': login_form,
            }
            messages.error(request, "Error en el formulario de entrevista. Por favor, revisa los campos.")
            return render(request, 'index.html', context) 
    else:
        # Si se accede por GET, redirige al inicio
        return redirect('inicio')


# Vista de registro
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 1. Guarda el objeto User
            user = form.save()
            
            # 2. Crea el objeto Perfil y asocia el User
            Perfil.objects.create(
                user=user,
                numero_documento=form.cleaned_data.get('numero_documento'),
                fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                domicilio=form.cleaned_data.get('domicilio'),
                telefono=form.cleaned_data.get('telefono'),
            )
            
            messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
            return redirect('login') 
        else:
             # Si el registro falla
            messages.error(request, "Error en el formulario de registro. Por favor, verifica los datos.")
    else:
        form = RegisterForm()
        
    return render(request, 'register.html', {'form': form}) 

def dashboard_view(request):
    return render(request, 'dashboard.html')

def turnos_view(request):
    return render(request, 'turnos.html')

def pacientes_list(request):
    pacientes = Paciente.objects.all()
    return render(request, 'pacientes/pacientes_list.html', {'pacientes': pacientes})



def paciente_create(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pacientes_list')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/pacientes_form.html', {'form': form})


def paciente_update(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('pacientes_list')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/pacientes_form.html', {'form': form})

def paciente_delete(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('pacientes_list') 
    
    return render(request, 'pacientes/paciente_confirm_delete.html', {'paciente': paciente})