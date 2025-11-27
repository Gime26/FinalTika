"""
Vistas de gestión de contactos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..decorators import solo_terapeutas
from ..models import Contacto

__all__ = [
    'lista_contactos', 'marcar_contacto_leido', 'marcar_contacto_respondido',
    'confirmar_eliminar_contacto', 'eliminar_contacto'
]


@login_required
@solo_terapeutas
def lista_contactos(request):
    """Lista de todos los mensajes de contacto"""
    contactos = Contacto.objects.all().order_by('-fecha_envio')
    
    # Contar por estado
    total = contactos.count()
    nuevos = contactos.filter(estado='nuevo').count()
    leidos = contactos.filter(estado='leido').count()
    respondidos = contactos.filter(estado='respondido').count()
    
    context = {
        'contactos': contactos,
        'total': total,
        'nuevos': nuevos,
        'leidos': leidos,
        'respondidos': respondidos,
    }
    
    return render(request, 'contactos/lista_contactos.html', context)


@login_required
@solo_terapeutas
def marcar_contacto_leido(request, contacto_id):
    """Marcar un contacto como leído"""
    if request.method == 'POST':
        try:
            contacto = get_object_or_404(Contacto, id=contacto_id)
            
            if contacto.estado == 'nuevo':
                contacto.estado = 'leido'
                contacto.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Contacto marcado como leído'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'El contacto ya está en estado: {contacto.get_estado_display()}'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@solo_terapeutas
def marcar_contacto_respondido(request, contacto_id):
    """Marcar un contacto como respondido"""
    if request.method == 'POST':
        try:
            contacto = get_object_or_404(Contacto, id=contacto_id)
            
            if contacto.estado != 'respondido':
                contacto.estado = 'respondido'
                contacto.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Contacto marcado como respondido'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'El contacto ya estaba marcado como respondido'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@solo_terapeutas
def confirmar_eliminar_contacto(request, contacto_id):
    """Vista de confirmación para eliminar contacto"""
    contacto = get_object_or_404(Contacto, id=contacto_id)
    return render(request, 'contactos/confirmar_eliminar.html', {'contacto': contacto})


@login_required
@solo_terapeutas
def eliminar_contacto(request, contacto_id):
    """Eliminar un contacto"""
    if request.method == 'POST':
        try:
            contacto = get_object_or_404(Contacto, id=contacto_id)
            contacto.delete()
            messages.success(request, 'Contacto eliminado exitosamente.')
            return redirect('lista_contactos')
        except Exception as e:
            messages.error(request, f'Error al eliminar contacto: {str(e)}')
            return redirect('lista_contactos')
    
    return redirect('lista_contactos')
