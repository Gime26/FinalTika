"""
Vistas de perfil de usuario
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from ..forms import PerfilUpdateForm
from ..models import Perfil

__all__ = ['mi_perfil', 'editar_perfil']


@login_required
def mi_perfil(request):
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado. Contacta a un administrador.")
        return redirect('login')
    
    return render(request, 'mi_perfil.html', {
        'perfil': perfil
    })


@login_required
def editar_perfil(request):
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado. Contacta a un administrador.")
        return redirect('login')
    
    advertencia = not perfil.matricula

    if request.method == 'POST':
        form = PerfilUpdateForm(request.POST, instance=perfil)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect('mi_perfil')
            except IntegrityError:
                messages.error(request, "Error: El DNI ingresado ya está asociado a otra cuenta.")
            except Exception as e:
                messages.error(request, f"Error al actualizar perfil: {str(e)}")
        else:
            messages.error(request, "Por favor, verifica los datos ingresados.")
    else:
        form = PerfilUpdateForm(instance=perfil)

    return render(request, 'editar_perfil.html', {
        'form': form,
        'advertencia': advertencia,
        'perfil': perfil
    })
