"""
Vistas de dashboard y página de inicio
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..decorators import solo_terapeutas
from ..models import Perfil, Paciente, Testimonio, Contacto

__all__ = ['inicio', 'dashboard', 'dashboard_terapeutas', 'dashboard_pacientes']


def inicio(request):
    """Página de inicio con testimonios y formulario de contacto"""
    # Procesar formulario de contacto si se envía
    if request.method == 'POST' and 'nombre' in request.POST:
        Contacto.objects.create(
            nombre=request.POST.get('nombre'),
            email=request.POST.get('email'),
            telefono=request.POST.get('telefono', ''),
            mensaje=request.POST.get('mensaje', '')
        )
        messages.success(request, '¡Gracias por contactarnos! Te responderemos pronto.')
        return redirect('/#contacto')
    
    testimonios = Testimonio.objects.filter(
        estado='aprobado',
        publicado=True
    ).order_by('-fecha_envio')

    return render(request, "index.html", {
        "testimonios": testimonios
    })


@solo_terapeutas
def dashboard_terapeutas(request):
    return render(request, 'dashboard.html')


@login_required
@solo_terapeutas
def dashboard(request):
    """Dashboard principal para especialistas"""
    total_pacientes = Paciente.objects.count()
    
    context = {
        'total_pacientes': total_pacientes,
    }
    return render(request, 'dashboard.html', context)


@login_required
def dashboard_pacientes(request):
    """Dashboard para pacientes"""
    try:
        perfil_del_usuario = request.user.perfil
    except:
        messages.error(request, "No se encontró tu perfil.")
        return redirect('login')
    
    if perfil_del_usuario.rol != 'paciente':
        messages.error(request, "Acceso denegado. Esta área es solo para pacientes.")
        return redirect('dashboard')
    
    return render(request, 'pacientes/dashboard_pacientes.html', {
        'perfil': perfil_del_usuario
    })
