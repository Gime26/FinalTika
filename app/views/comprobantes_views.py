"""
Vistas de comprobantes
"""
from django.shortcuts import render

from ..models import Paciente

__all__ = ['comprobantes_view']


def comprobantes_view(request):
    """Vista de comprobantes"""
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    return render(request, 'comprobantes.html', {'pacientes': pacientes})
