"""
Vistas de gestión de turnos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date
import json
import re
import traceback

from ..decorators import solo_terapeutas
from ..models import Turno, Paciente, Especialista, STATUS_CHOICES, Perfil

__all__ = [
    'gestion_turnos', 'crear_turno', 'editar_turno',
    'confirmar_turno', 'cancelar_turno', 'eliminar_turno',
    'turnos_view', 'gestionturnos'
]


@login_required
@solo_terapeutas
def gestion_turnos(request):
    """Vista principal para gestionar turnos"""
    turnos = Turno.objects.all().select_related('paciente', 'especialista').order_by('-fecha', '-hora')
    especialistas = Especialista.objects.all()
    
    # Obtener o crear el Especialista del usuario actual
    especialista_usuario = None
    try:
        perfil = request.user.perfil
        if perfil.rol == 'especialista':
            especialista_usuario, created = Especialista.objects.get_or_create(
                perfil=perfil,
                defaults={
                    'nombre': f"{perfil.nombre} {perfil.apellido}",
                    'especialidad': perfil.especialidad or "No especificado",
                    'matricula': perfil.matricula,
                    'email': perfil.email,
                    'telefono': perfil.telefono
                }
            )
            # Filtrar turnos solo del especialista actual
            turnos = turnos.filter(especialista=especialista_usuario)
    except:
        pass
    
    # Preparar turnos como JSON para JavaScript
    turnos_json = json.dumps([
        {
            'id': t.id,
            'fecha': t.fecha.strftime('%Y-%m-%d'),
            'hora': t.hora.strftime('%H:%M'),
            'especialista_id': t.especialista.id,
            'status': t.status,
            'motivo': t.motivo or ''
        }
        for t in turnos
    ])
    
    context = {
        'turnos': turnos,
        'especialistas': especialistas,
        'especialista_usuario': especialista_usuario,
        'status_choices': STATUS_CHOICES,
        'turnos_json': turnos_json,
        'today': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'Turnos/gestion_turnos.html', context)


@csrf_exempt
def crear_turno(request):
    """Crear un nuevo turno"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        # Validar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Usuario no autenticado'})
        
        # Validar que el usuario sea especialista
        try:
            perfil = request.user.perfil
        except AttributeError:
            return JsonResponse({'success': False, 'error': 'Usuario no tiene perfil asociado'})
        
        if perfil.rol != 'especialista':
            return JsonResponse({'success': False, 'error': 'Solo los especialistas pueden crear turnos'})
        
        # Buscar o crear el Especialista asociado al perfil
        especialista_usuario, created = Especialista.objects.get_or_create(
            perfil=perfil,
            defaults={
                'nombre': f"{perfil.nombre} {perfil.apellido}",
                'especialidad': perfil.especialidad or "No especificado",
                'matricula': perfil.matricula,
                'email': perfil.email,
                'telefono': perfil.telefono
            }
        )
        
        data = json.loads(request.body)
        
        # Buscar o crear paciente por DNI
        dni = data.get('dni_paciente', '').strip()
        nombre = data.get('nombre_paciente', '').strip()
        apellido = data.get('apellido_paciente', '').strip()
        
        if not dni or not nombre or not apellido:
            return JsonResponse({'success': False, 'error': 'DNI, nombre y apellido son obligatorios'})
        
        # Validar que el DNI tenga exactamente 8 dígitos
        if not re.match(r'^\d{8}$', dni):
            return JsonResponse({'success': False, 'error': 'El DNI debe contener exactamente 8 dígitos numéricos'})
        
        # Buscar paciente existente o crear nuevo
        paciente, created = Paciente.objects.get_or_create(
            dni=dni,
            defaults={'nombre': nombre, 'apellido': apellido}
        )
        
        # Si ya existe pero con diferente nombre, actualizamos
        if not created:
            if paciente.nombre != nombre or paciente.apellido != apellido:
                paciente.nombre = nombre
                paciente.apellido = apellido
                paciente.save()
        
        # USAR EL ESPECIALISTA DEL USUARIO ACTUAL
        especialista = especialista_usuario
        fecha = data.get('fecha')
        
        # Validar que el paciente no tenga otro turno con el mismo especialista el mismo día
        turno_existente = Turno.objects.filter(
            paciente=paciente,
            especialista=especialista,
            fecha=fecha
        ).exclude(status='CANCELLED').first()
        
        if turno_existente:
            return JsonResponse({
                'success': False,
                'error': f'El paciente ya tiene un turno contigo el {fecha} a las {turno_existente.hora.strftime("%H:%M")}.'
            })
        
        # Crear el turno
        turno = Turno(
            paciente=paciente,
            especialista=especialista,
            fecha=fecha,
            hora=data.get('hora'),
            motivo=data.get('motivo', ''),
            creado_por=request.user
        )
        
        turno.full_clean()
        turno.save()
        
        print(f"✅ TURNO GUARDADO: ID={turno.id}, Paciente={turno.paciente}, Fecha={turno.fecha}, Hora={turno.hora}")
        
        return JsonResponse({
            'success': True,
            'message': 'Turno creado exitosamente',
            'turno': {
                'id': turno.id,
                'paciente': f"{turno.paciente.nombre} {turno.paciente.apellido}",
                'paciente_dni': turno.paciente.dni,
                'especialista': turno.especialista.nombre,
                'fecha': turno.fecha.strftime('%Y-%m-%d'),
                'hora': turno.hora.strftime('%H:%M'),
                'motivo': turno.motivo,
                'status': turno.get_status_display()
            }
        })
        
    except Especialista.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'El profesional seleccionado no existe'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Error al parsear los datos JSON'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error inesperado: {str(e)}',
            'traceback': traceback.format_exc()
        })


@login_required
def editar_turno(request, pk):
    """Editar un turno existente - placeholder, necesita implementación completa"""
    turno = get_object_or_404(Turno, pk=pk)
    messages.info(request, 'Función de editar turno en desarrollo')
    return redirect('gestion_turnos')


@login_required
@solo_terapeutas
def confirmar_turno(request, pk):
    """Confirmar un turno"""
    if request.method == 'POST':
        turno = get_object_or_404(Turno, pk=pk)
        turno.status = 'CONFIRMED'
        turno.save()
        return JsonResponse({'success': True, 'message': f'Turno confirmado para {turno.paciente.nombre}'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@solo_terapeutas
def cancelar_turno(request, pk):
    """Cancelar un turno"""
    if request.method == 'POST':
        turno = get_object_or_404(Turno, pk=pk)
        turno.status = 'CANCELLED'
        turno.save()
        return JsonResponse({'success': True, 'message': 'Turno cancelado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@solo_terapeutas
def eliminar_turno(request, pk):
    """Eliminar un turno"""
    if request.method == 'POST':
        turno = get_object_or_404(Turno, pk=pk)
        turno.delete()
        return JsonResponse({'success': True, 'message': 'Turno eliminado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# Vistas legacy (mantener por compatibilidad)
def turnos_view(request):
    return redirect('gestion_turnos')


def gestionturnos(request):
    return redirect('gestion_turnos')
