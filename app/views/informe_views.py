"""
Vistas de gestión de informes interdisciplinarios
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..decorators import solo_terapeutas
from ..models import InformeInterdisciplinario, SeccionInforme
from ..forms import InformeInterdisciplinarioForm, SeccionInformeForm

__all__ = [
    'crear_informe_interdisciplinario', 'lista_informes', 'detalle_informe',
    'agregar_seccion_informe', 'editar_informe', 'eliminar_informe',
    'eliminar_seccion_informe'
]


@login_required
def crear_informe_interdisciplinario(request):
    """Crear un nuevo informe interdisciplinario"""
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden crear informes.")
            return redirect('dashboard')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = InformeInterdisciplinarioForm(request.POST)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.creado_por = request.user
            informe.save()
            form.save_m2m()  # Guardar relación ManyToMany de especialistas
            messages.success(request, f'Informe creado exitosamente para {informe.paciente}')
            return redirect('lista_informes')
    else:
        form = InformeInterdisciplinarioForm()

    return render(request, 'informes/crear_informe.html', {'form': form})


@login_required
def lista_informes(request):
    """Lista todos los informes (especialistas ven todos, pacientes ven solo los suyos)"""
    try:
        perfil = request.user.perfil
        
        if perfil.rol == 'especialista':
            # Especialistas ven todos los informes o los que colaboran
            informes = InformeInterdisciplinario.objects.all().prefetch_related('especialistas', 'paciente')
        else:
            # Pacientes ven solo sus informes
            if perfil.paciente:
                informes = InformeInterdisciplinario.objects.filter(paciente=perfil.paciente).prefetch_related('especialistas')
            else:
                informes = []
                messages.info(request, "No tienes informes asociados.")
        
        return render(request, 'informes/lista_informes.html', {'informes': informes})
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')


@login_required
def detalle_informe(request, informe_id):
    """Ver detalle de un informe con todas las secciones de los especialistas"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    # Verificar permisos
    try:
        perfil = request.user.perfil
        
        # Pacientes solo pueden ver sus propios informes
        if perfil.rol == 'paciente':
            if not perfil.paciente or informe.paciente != perfil.paciente:
                messages.error(request, "No tienes permiso para ver este informe.")
                return redirect('paciente_informes')
            
            # Obtener secciones para pacientes
            secciones = informe.secciones.all().select_related('especialista')
            
            context = {
                'informe': informe,
                'secciones': secciones,
            }
            
            # Usar template de pacientes
            return render(request, 'pacientes/detalle_informe_paciente.html', context)
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
    # Obtener todas las secciones del informe (para especialistas)
    secciones = informe.secciones.all().select_related('especialista')
    
    # Verificar si el usuario actual es colaborador y si ya tiene una sección
    es_colaborador = False
    tiene_seccion = False
    
    if perfil.rol == 'especialista':
        es_colaborador = informe.especialistas.filter(pk=perfil.pk).exists()
        tiene_seccion = secciones.filter(especialista=perfil).exists()
    
    context = {
        'informe': informe,
        'secciones': secciones,
        'es_colaborador': es_colaborador,
        'tiene_seccion': tiene_seccion,
    }
    
    return render(request, 'informes/detalle_informe.html', context)


@login_required
def agregar_seccion_informe(request, informe_id):
    """Permite a un especialista agregar o editar su sección en el informe"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    try:
        perfil = request.user.perfil
        
        # Solo especialistas pueden agregar secciones
        if perfil.rol != 'especialista':
            messages.error(request, "Solo especialistas pueden agregar contenido a los informes.")
            return redirect('detalle_informe', informe_id=informe_id)
        
        # Verificar que sea un colaborador del informe
        if not informe.especialistas.filter(pk=perfil.pk).exists():
            messages.error(request, "No eres colaborador de este informe.")
            return redirect('detalle_informe', informe_id=informe_id)
        
        # Buscar si ya tiene una sección creada
        seccion, created = SeccionInforme.objects.get_or_create(
            informe=informe,
            especialista=perfil
        )
        
        if request.method == 'POST':
            form = SeccionInformeForm(request.POST, instance=seccion)
            if form.is_valid():
                form.save()
                action = "agregada" if created else "actualizada"
                messages.success(request, f'Tu sección ha sido {action} exitosamente.')
                return redirect('detalle_informe', informe_id=informe_id)
        else:
            form = SeccionInformeForm(instance=seccion)
        
        context = {
            'form': form,
            'informe': informe,
            'es_edicion': not created
        }
        
        return render(request, 'informes/agregar_seccion.html', context)
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')


@login_required
def editar_informe(request, informe_id):
    """Editar un informe interdisciplinario (solo el creador)"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden editar informes.")
            return redirect('dashboard')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
    # Solo el creador puede editar el informe base
    if informe.creado_por != request.user:
        messages.error(request, "Solo el especialista que creó este informe puede editarlo.")
        return redirect('detalle_informe', informe_id=informe_id)
    
    if request.method == 'POST':
        form = InformeInterdisciplinarioForm(request.POST, instance=informe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informe actualizado exitosamente.')
            return redirect('detalle_informe', informe_id=informe_id)
    else:
        form = InformeInterdisciplinarioForm(instance=informe)
    
    return render(request, 'informes/editar_informe.html', {
        'form': form,
        'informe': informe
    })


@login_required
def eliminar_informe(request, informe_id):
    """Eliminar un informe (solo el creador)"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden eliminar informes.")
            return redirect('dashboard')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
    # Solo el creador puede eliminar
    if informe.creado_por != request.user:
        messages.error(request, "Solo el especialista que creó este informe puede eliminarlo.")
        return redirect('lista_informes')
    
    if request.method == 'POST':
        paciente_nombre = str(informe.paciente)
        informe.delete()
        messages.success(request, f'Informe de {paciente_nombre} eliminado exitosamente.')
        return redirect('lista_informes')
    
    return render(request, 'informes/informe_confirm_delete.html', {
        'informe': informe
    })


@login_required
def eliminar_seccion_informe(request, seccion_id):
    """Eliminar una sección de informe (solo el autor de la sección)"""
    seccion = get_object_or_404(SeccionInforme, pk=seccion_id)
    
    try:
        perfil = request.user.perfil
        
        # Solo el autor de la sección puede eliminarla
        if seccion.especialista != perfil:
            messages.error(request, "Solo puedes eliminar tus propias secciones.")
            return redirect('detalle_informe', informe_id=seccion.informe.id)
        
        informe_id = seccion.informe.id
        
        if request.method == 'POST':
            seccion.delete()
            messages.success(request, 'Tu sección ha sido eliminada.')
            return redirect('detalle_informe', informe_id=informe_id)
        
        return render(request, 'informes/seccion_confirm_delete.html', {
            'seccion': seccion
        })
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('lista_informes')
