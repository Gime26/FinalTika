"""
Vistas de gestión de entrevistas de admisión
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date, time
import json
import re

from ..decorators import solo_terapeutas
from ..models import Entrevista, Paciente, Especialista

__all__ = [
    'entrevista_view', 'gestion_entrevistas', 'ver_entrevista', 'derivar_entrevista'
]


def entrevista_view(request):
    """Formulario público para solicitar entrevista de admisión"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            dni_paciente = request.POST.get('dni_paciente', '').strip()
            nombre_paciente = request.POST.get('nombre_paciente', '').strip()
            apellido_paciente = request.POST.get('apellido_paciente', '').strip()
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            telefono = request.POST.get('telefono_contacto', '').strip()
            
            # Recopilar información adicional (pasos 2, 3, 4)
            datos_prenatales = request.POST.get('datos_prenatales', '')
            datos_escolares = request.POST.get('datos_escolares', '')
            datos_clinicos = request.POST.get('datos_clinicos', '')
            
            # Combinar motivo de consulta con todos los datos
            motivo_consulta = f"""
DATOS DEL TUTOR:
{request.POST.get('nombre_tutor', '')}
Teléfono: {telefono}

ETAPA PRENATAL Y PERINATAL:
{datos_prenatales}

ETAPA ESCOLAR:
{datos_escolares}

ANTECEDENTES CLÍNICOS:
{datos_clinicos}
            """.strip()
            
            # Validación de DNI (8 dígitos)
            if not re.match(r'^\d{8}$', dni_paciente):
                messages.error(request, "El DNI debe contener exactamente 8 dígitos numéricos.")
                return redirect('entrevista')
            
            # Validación básica
            if not all([dni_paciente, nombre_paciente, apellido_paciente]):
                messages.error(request, "Por favor complete todos los campos obligatorios del paso 1.")
                return redirect('entrevista')
            
            # Buscar o crear paciente
            paciente, created = Paciente.objects.get_or_create(
                dni=dni_paciente,
                defaults={
                    'nombre': nombre_paciente,
                    'apellido': apellido_paciente,
                    'fecha_nacimiento': fecha_nacimiento if fecha_nacimiento else None,
                    'telefono': telefono
                }
            )
            
            # Si el paciente ya existe, actualizar sus datos
            if not created:
                paciente.nombre = nombre_paciente
                paciente.apellido = apellido_paciente
                if fecha_nacimiento:
                    paciente.fecha_nacimiento = fecha_nacimiento
                if telefono:
                    paciente.telefono = telefono
                paciente.save()
            
            # Crear la entrevista (fecha y hora se asignarán después por los especialistas)
            entrevista = Entrevista.objects.create(
                paciente=paciente,
                fecha=date.today(),  # Fecha de recepción
                hora=time(9, 0),  # Hora por defecto, se modificará luego
                motivo_consulta=motivo_consulta
            )
            
            messages.success(request, f"¡Entrevista de admisión recibida correctamente! Gracias {nombre_paciente} {apellido_paciente}. Nuestros especialistas revisarán la información y nos pondremos en contacto para confirmar la cita y asignar el profesional más adecuado.")
            return redirect('index')
            
        except Exception as e:
            messages.error(request, f"Error al procesar la entrevista: {str(e)}")
            return redirect('entrevista')
    else:
        # Mostrar el formulario wizard cuando se accede por GET
        return render(request, 'entrevista_publica.html')


@login_required
@solo_terapeutas
def gestion_entrevistas(request):
    """Vista para que los especialistas gestionen las entrevistas de admisión"""
    entrevistas = Entrevista.objects.select_related('paciente', 'especialista_asignado').order_by('-fecha_creacion')
    especialistas = Especialista.objects.all()
    
    # Contar por estado
    total = entrevistas.count()
    pendientes = entrevistas.filter(estado='pendiente').count()
    en_revision = entrevistas.filter(estado='en_revision').count()
    derivadas = entrevistas.filter(estado='derivada').count()
    
    context = {
        'entrevistas': entrevistas,
        'especialistas': especialistas,
        'total': total,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'derivadas': derivadas,
    }
    
    return render(request, 'entrevistas/gestion_entrevistas.html', context)


@login_required
@solo_terapeutas
def ver_entrevista(request, pk):
    """Ver detalles completos de una entrevista"""
    entrevista = get_object_or_404(Entrevista, pk=pk)
    especialistas = Especialista.objects.all()
    
    context = {
        'entrevista': entrevista,
        'especialistas': especialistas,
    }
    
    return render(request, 'entrevistas/ver_entrevista.html', context)


@login_required
@solo_terapeutas
def derivar_entrevista(request, pk):
    """Asignar especialista y cambiar estado de entrevista"""
    if request.method == 'POST':
        try:
            entrevista = get_object_or_404(Entrevista, pk=pk)
            data = json.loads(request.body)
            
            especialista_id = data.get('especialista_id')
            estado = data.get('estado')
            observaciones = data.get('observaciones', '')
            
            if especialista_id:
                especialista = Especialista.objects.get(id=especialista_id)
                entrevista.especialista_asignado = especialista
            
            if estado:
                entrevista.estado = estado
            
            if observaciones:
                entrevista.observaciones = observaciones
            
            entrevista.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Entrevista actualizada correctamente'
            })
            
        except Especialista.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'El especialista seleccionado no existe'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
