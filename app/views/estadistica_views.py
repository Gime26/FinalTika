"""
Vistas de estadísticas
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count
from django.views.decorators.csrf import csrf_exempt
import json

from ..models import EstadisticaPaciente

__all__ = ['estadistica_view', 'estadistica_agregar']


def estadistica_view(request):
    """Vista principal de estadísticas"""
    pacientes = EstadisticaPaciente.objects.all().order_by("-fecha_registro")
    total = pacientes.count()
    promedio_edad = pacientes.aggregate(prom=Avg("edad"))["prom"] or 0

    conteo = EstadisticaPaciente.objects.values("especialidad").annotate(total=Count("id"))

    return render(request, "estadistica.html", {
        "pacientes": pacientes,
        "total": total,
        "promedio": round(promedio_edad, 1),
        "conteo": list(conteo)
    })


@csrf_exempt
def estadistica_agregar(request):
    """Agregar un paciente a las estadísticas"""
    if request.method == "POST":
        data = json.loads(request.body)

        nombre = data.get("nombre")
        edad = data.get("edad")
        especialidad = data.get("especialidad")

        nuevo = EstadisticaPaciente.objects.create(
            nombre=nombre,
            edad=edad,
            especialidad=especialidad
        )

        return JsonResponse({"status": "ok", "id": nuevo.id})

    return JsonResponse({"error": "Método no permitido"}, status=400)
