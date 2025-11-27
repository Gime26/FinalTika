"""
Vistas de autenticación y registro
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from ..forms import LoginForm, RegisterForm
from ..models import Perfil

__all__ = ['login_view', 'logout_view', 'register_view', 'base']


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido {user.username}!")
                
                try:
                    perfil = user.perfil
                    if perfil.rol == 'especialista':
                        return redirect('dashboard')
                    elif perfil.rol == 'paciente':
                        return redirect('dashboard_pacientes')
                    else:
                        return redirect('dashboard')
                except Perfil.DoesNotExist:
                    messages.error(request, "Tu cuenta no tiene un perfil asignado. Contacta al administrador.")
                    logout(request)
                    return redirect('login')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Por favor, verifica los datos ingresados.")
    else:
        form = LoginForm()
    
    return render(request, "login.html", {"form": form})


def logout_view(request):
    """Cerrar sesión del usuario"""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('inicio')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    
                    Perfil.objects.create(
                        user=user,
                        nombre=form.cleaned_data.get('nombre', ''),
                        apellido=form.cleaned_data.get('apellido', ''),
                        dni=form.cleaned_data.get('dni', ''),
                        telefono=form.cleaned_data.get('telefono', ''),
                        email=user.email,
                        rol=form.cleaned_data.get('rol', 'paciente')
                    )
                    
                    messages.success(request, "Usuario creado exitosamente. Ya puedes iniciar sesión.")
                    return redirect('login')
            except IntegrityError:
                messages.error(request, "Error: El DNI o nombre de usuario ya están registrados.")
            except Exception as e:
                messages.error(request, f"Error al crear usuario: {str(e)}")
        else:
            messages.error(request, "Por favor, verifica los datos ingresados.")
    else:
        form = RegisterForm()
    
    return render(request, 'registro.html', {'form': form})


def base(request):
    return render(request, "base.html")
