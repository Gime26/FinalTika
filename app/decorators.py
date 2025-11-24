from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def solo_terapeutas(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.perfil.rol != 'terapeuta':
            return redirect('dashboard_pacientes')   # o a donde quieras mandarlo
        return view_func(request, *args, **kwargs)
    return wrapper


def solo_pacientes(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.perfil.rol != 'paciente':
            return redirect('dashboard_terapeutas')
        return view_func(request, *args, **kwargs)
    return wrapper
