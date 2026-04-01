"""
Vistas de gestión de testimonios
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Testimonio
from ..forms import TestimonioForm

__all__ = [
    'enviar_testimonio', 'testimonios_publicos', 'testimonios_lista',
    'aprobar_testimonio', 'restringir_testimonio', 'editar_testimonio',
    'eliminar_testimonio', 'testimonios_inicio'
]


def enviar_testimonio(request):
    """Formulario público para enviar testimonios"""
    if request.method == 'POST':
        form = TestimonioForm(request.POST, request.FILES)
        if form.is_valid():
            testimonio = form.save(commit=False)
            testimonio.usuario = request.user if request.user.is_authenticated else None
            testimonio.estado = "pendiente"
            testimonio.publicado = False
            testimonio.save()
            messages.success(request, 'Testimonio enviado exitosamente. Será revisado por nuestro equipo.')
            return redirect('index')
    else:
        form = TestimonioForm()

    return render(request, 'testimonio/enviar_testimonio.html', {'form': form})


def testimonios_publicos(request):
    """Vista pública de testimonios aprobados"""
    testimonios = Testimonio.objects.filter(
        estado='aprobado',
        publicado=True
    ).order_by('-fecha_envio')

    return render(request, 'testimonios_publicos.html', {'testimonios': testimonios})


@login_required
def testimonios_lista(request):
    """Lista de todos los testimonios (dashboard especialistas)"""
    testimonios = Testimonio.objects.all().order_by('-fecha_envio')
    return render(request, 'dashboard/testimonios.html', {'testimonios': testimonios})


@login_required
def aprobar_testimonio(request, id):
    """Aprobar un testimonio para publicación"""
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.estado = 'aprobado'
    testimonio.publicado = True
    testimonio.save()
    messages.success(request, f'Testimonio de {testimonio.usuario.username} aprobado exitosamente.')
    return redirect('testimonios_lista')


@login_required
def restringir_testimonio(request, id):
    """Restringir un testimonio (no publicado)"""
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.estado = 'restringido'
    testimonio.publicado = False
    testimonio.save()
    messages.warning(request, f'Testimonio de {testimonio.nombre_autor} restringido.')
    return redirect('testimonios_lista')


@login_required
def editar_testimonio(request, id):
    """Editar un testimonio"""
    testimonio = get_object_or_404(Testimonio, id=id)
    if request.method == 'POST':
        form = TestimonioForm(request.POST, request.FILES, instance=testimonio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonio actualizado exitosamente.')
            return redirect('testimonios_lista')
    else:
        form = TestimonioForm(instance=testimonio)
    
    return render(request, 'testimonio/editar_testimonio.html', {
        'form': form,
        'testimonio': testimonio
    })


@login_required
def eliminar_testimonio(request, id):
    """Eliminar un testimonio"""
    testimonio = get_object_or_404(Testimonio, id=id)
    if request.method == 'POST':
        testimonio.delete()
        messages.success(request, 'Testimonio eliminado exitosamente.')
        return redirect('testimonios_lista')
    return render(request, 'testimonio/eliminar_testimonio.html', {
        'testimonio': testimonio
    })


def testimonios_inicio(request):
    """Testimonios para la página de inicio"""
    testimonios = Testimonio.objects.filter(
        estado='aprobado',
        publicado=True
    ).order_by('-fecha_envio')

    return render(request, 'testimonio/test_public.html', {'testimonios': testimonios})
