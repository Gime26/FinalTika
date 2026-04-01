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
    
    # Buscar la última fecha de backup
    import os
    import re
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
    ultima_backup = None
    if os.path.exists(BACKUP_DIR):
        backups = [d for d in os.listdir(BACKUP_DIR) if re.match(r'backup_\d{8}_\d{6}', d)]
        if backups:
            backups.sort(reverse=True)
            fecha_str = backups[0].replace('backup_', '').replace('_', ' ')
            # Formatear fecha para mostrar bonito
            try:
                from datetime import datetime
                dt = datetime.strptime(fecha_str, '%Y%m%d %H%M%S')
                ultima_backup = dt.strftime('%d/%m/%Y %H:%M')
            except Exception:
                ultima_backup = fecha_str
    return render(request, 'mi_perfil.html', {
        'perfil': perfil,
        'ultima_backup': ultima_backup
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
