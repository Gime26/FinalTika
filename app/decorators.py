from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def solo_terapeutas(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.perfil.rol != 'especialista':
                messages.error(request, 'Acceso denegado. Solo especialistas pueden acceder a esta sección.')
                return redirect('dashboard_pacientes')
        except:
            messages.error(request, 'Error de permisos.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def solo_pacientes(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.perfil.rol != 'paciente':
                messages.error(request, 'Acceso denegado. Solo pacientes pueden acceder a esta sección.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Error de permisos.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
