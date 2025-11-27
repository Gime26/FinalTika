"""
Vistas de gestión de pacientes
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone

from ..decorators import solo_terapeutas
from ..models import Paciente, Observacion, InformeInterdisciplinario
from ..forms import PacienteForm

__all__ = [
    'pacientes_list', 'paciente_create', 'paciente_update', 'paciente_delete',
    'dashboard_pacientes', 'paciente_turnos', 'paciente_informes',
    'paciente_observaciones', 'paciente_comprobantes', 'paciente_perfil'
]


@login_required
@solo_terapeutas
def pacientes_list(request):
    """Lista todos los pacientes"""
    pacientes = Paciente.objects.all()
    return render(request, "pacientes/pacientes_list.html", {"pacientes": pacientes})


@login_required
@solo_terapeutas
def paciente_create(request):
    """Crear un nuevo paciente"""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente creado exitosamente.')
            return redirect('pacientes_list')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/pacientes_form.html', {'form': form})


@login_required
@solo_terapeutas
def paciente_update(request, pk):
    """Editar un paciente existente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado exitosamente.')
            return redirect('pacientes_list')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/pacientes_form.html', {'form': form})


@login_required
@solo_terapeutas
def paciente_delete(request, pk):
    """Eliminar un paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado exitosamente.')
        return redirect('pacientes_list')
    
    return render(request, 'pacientes/paciente_confirm_delete.html', {'paciente': paciente})


@login_required
def dashboard_pacientes(request):
    """Dashboard principal para pacientes"""
    try:
        perfil = request.user.perfil
        
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        paciente = perfil.paciente
        
        context = {
            'paciente': paciente,
        }
        
        return render(request, "pacientes/dashboard_pacientes.html", context)
    
    except Exception as e:
        messages.error(request, f"Error al cargar dashboard: {str(e)}")
        return redirect('login')


@login_required
def paciente_turnos(request):
    """Ver turnos del paciente"""
    try:
        perfil = request.user.perfil
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        from ..models import Turno
        turnos = Turno.objects.filter(paciente=perfil.paciente).order_by('-fecha', '-hora')
        
        return render(request, "pacientes/paciente_turnos.html", {
            'turnos': turnos,
            'paciente': perfil.paciente
        })
    except Exception as e:
        messages.error(request, f"Error al cargar turnos: {str(e)}")
        return redirect('dashboard_pacientes')


@login_required
def paciente_informes(request):
    """Ver informes del paciente"""
    try:
        perfil = request.user.perfil
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        informes = InformeInterdisciplinario.objects.filter(
            paciente=perfil.paciente
        ).prefetch_related('especialistas')
        
        return render(request, "pacientes/paciente_informes.html", {
            'informes': informes,
            'paciente': perfil.paciente
        })
    except Exception as e:
        messages.error(request, f"Error al cargar informes: {str(e)}")
        return redirect('dashboard_pacientes')


@login_required
def paciente_observaciones(request):
    """Ver observaciones del paciente"""
    try:
        perfil = request.user.perfil
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        observaciones = Observacion.objects.filter(
            paciente=perfil.paciente
        ).order_by('-fecha')
        
        # Marcar las nuevas (últimos 7 días)
        hace_7_dias = timezone.now() - timedelta(days=7)
        
        for obs in observaciones:
            obs.es_nueva = obs.fecha_registro and obs.fecha_registro >= hace_7_dias
        
        return render(request, "pacientes/paciente_observaciones.html", {
            'observaciones': observaciones,
            'paciente': perfil.paciente
        })
    except:
        messages.error(request, "Error al cargar observaciones.")
        return redirect('dashboard_pacientes')


@login_required
def paciente_comprobantes(request):
    """Ver comprobantes del paciente"""
    try:
        perfil = request.user.perfil
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        # Por ahora solo renderizar el template
        # Cuando implementes comprobantes, aquí filtrarás por paciente
        return render(request, "pacientes/paciente_comprobantes.html", {
            'paciente': perfil.paciente
        })
    except:
        messages.error(request, "Error al cargar comprobantes.")
        return redirect('dashboard_pacientes')


@login_required
def paciente_perfil(request):
    """Ver perfil del paciente"""
    return render(request, "pacientes/paciente_perfil.html")
