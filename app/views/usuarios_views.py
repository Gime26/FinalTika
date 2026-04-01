from django.shortcuts import render
from app.models import Especialista

from app.models import Entrevista

def usuarios_registrados(request):
    especialistas = Especialista.objects.all()
    mensaje = None
    entrevista_id = request.GET.get('entrevista_id')
    entrevista = Entrevista.objects.filter(id=entrevista_id).first() if entrevista_id else None
    if request.method == 'POST' and entrevista:
        especialista_id = request.POST.get('especialista_id')
        especialista = Especialista.objects.filter(id=especialista_id).first()
        if especialista:
            entrevista.especialista_asignado = especialista
            entrevista.estado = 'derivada'
            entrevista.save()
            mensaje = f"Entrevista derivada a {especialista.nombre} ({especialista.especialidad}) correctamente."
    return render(request, 'usuarios_registrados.html', {'especialistas': especialistas, 'mensaje': mensaje})
