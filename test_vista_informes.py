import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.models import InformeInterdisciplinario, User
from datetime import datetime, timedelta

# Buscar usuario agustina
user = User.objects.filter(username='agustina').first()
print(f"Usuario: {user}")

if user and hasattr(user, 'perfil'):
    perfil = user.perfil
    print(f"Perfil: {perfil}")
    print(f"Rol: {perfil.rol}")
    print(f"Paciente: {perfil.paciente}")
    
    if perfil.rol == 'paciente' and perfil.paciente:
        print("\n✓ Validaciones pasadas")
        
        # Query de informes (mismo que en la vista)
        informes = InformeInterdisciplinario.objects.filter(
            paciente=perfil.paciente
        ).prefetch_related('especialistas', 'secciones').order_by('-fecha_informe')
        
        print(f"\nTotal informes encontrados: {informes.count()}")
        
        # Marcar los nuevos
        from django.utils import timezone
        hace_7_dias = timezone.now() - timedelta(days=7)
        print(f"Fecha hace 7 días: {hace_7_dias}")
        
        for informe in informes:
            es_nuevo = informe.fecha_creacion and informe.fecha_creacion >= hace_7_dias
            print(f"\nInforme: {informe.asunto}")
            print(f"  - Fecha informe: {informe.fecha_informe}")
            print(f"  - Fecha creación: {informe.fecha_creacion}")
            print(f"  - Es nuevo: {es_nuevo}")
            print(f"  - Descripción: {informe.descripcion_general[:50] if informe.descripcion_general else 'Sin descripción'}")
            print(f"  - Especialistas: {list(informe.especialistas.all())}")
    else:
        print(f"\n✗ Validación falló:")
        print(f"  - Rol es paciente: {perfil.rol == 'paciente'}")
        print(f"  - Tiene paciente: {perfil.paciente is not None}")
