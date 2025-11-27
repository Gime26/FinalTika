"""
Vistas de gestión de observaciones
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy

from ..models import Observacion
from ..forms import ObservacionForm

__all__ = [
    'ListaObservacionesView', 'CrearObservacionView',
    'editar_observacion', 'eliminar_observacion'
]


class ListaObservacionesView(LoginRequiredMixin, ListView):
    """Lista de observaciones"""
    model = Observacion
    template_name = 'observaciones/observacion_list.html'
    context_object_name = 'observaciones'
    ordering = ['-fecha']


class CrearObservacionView(LoginRequiredMixin, CreateView):
    """Crear nueva observación"""
    model = Observacion
    form_class = ObservacionForm
    template_name = 'observaciones/observacion_form.html'
    success_url = reverse_lazy('lista_observaciones')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Prellenar especialista con el usuario actual
        try:
            perfil = self.request.user.perfil
            # Buscar el valor del especialista basado en el perfil
            for choice_value, choice_label in Observacion.ESPECIALISTAS:
                if perfil.nombre.lower() in choice_label.lower() or perfil.apellido.lower() in choice_label.lower():
                    form.fields['especialista'].initial = choice_value
                    break
        except:
            pass
        return form

    def form_valid(self, form):
        form.instance.creada_por = self.request.user
        # Asegurar que el especialista sea el del usuario actual
        try:
            perfil = self.request.user.perfil
            for choice_value, choice_label in Observacion.ESPECIALISTAS:
                if perfil.nombre.lower() in choice_label.lower() or perfil.apellido.lower() in choice_label.lower():
                    form.instance.especialista = choice_value
                    break
        except:
            pass
        return super().form_valid(form)


@login_required
def editar_observacion(request, pk):
    """Editar una observación existente"""
    observacion = get_object_or_404(Observacion, pk=pk)
    
    # Solo el creador puede editar
    if observacion.creada_por != request.user:
        messages.error(request, "Solo el especialista que creó esta observación puede editarla.")
        return redirect('lista_observaciones')
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden editar observaciones.")
            return redirect('lista_observaciones')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('lista_observaciones')
    
    if request.method == 'POST':
        form = ObservacionForm(request.POST, instance=observacion)
        if form.is_valid():
            # Forzar que el especialista siga siendo el mismo (del creador original)
            observacion_actualizada = form.save(commit=False)
            # Mantener el especialista original, no permitir cambios
            observacion_actualizada.especialista = observacion.especialista
            observacion_actualizada.save()
            messages.success(request, 'Observación actualizada exitosamente.')
            return redirect('lista_observaciones')
    else:
        form = ObservacionForm(instance=observacion)
        # Prellenar y deshabilitar el campo especialista
        form.fields['especialista'].initial = observacion.especialista
    
    return render(request, 'observaciones/observacion_form.html', {
        'form': form,
        'es_edicion': True,
        'observacion': observacion
    })


@login_required
def eliminar_observacion(request, pk):
    """Eliminar una observación"""
    observacion = get_object_or_404(Observacion, pk=pk)
    
    # Solo el creador puede eliminar
    if observacion.creada_por != request.user:
        messages.error(request, "Solo el especialista que creó esta observación puede eliminarla.")
        return redirect('lista_observaciones')
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden eliminar observaciones.")
            return redirect('lista_observaciones')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('lista_observaciones')
    
    if request.method == 'POST':
        observacion.delete()
        messages.success(request, 'Observación eliminada exitosamente.')
        return redirect('lista_observaciones')
    
    return render(request, 'observaciones/observacion_confirm_delete.html', {
        'observacion': observacion
    })
