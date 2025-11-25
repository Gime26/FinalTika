import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Perfil, Paciente

print("\n=== USUARIOS Y PERFILES ===")
for user in User.objects.all():
    try:
        perfil = user.perfil
        paciente_asociado = perfil.paciente is not None
        print(f"👤 Usuario: {user.username}")
        print(f"   - Rol: {perfil.rol}")
        print(f"   - Tiene Paciente asociado: {paciente_asociado}")
        if not paciente_asociado and perfil.rol == 'paciente':
            print(f"   ⚠️ PROBLEMA: Este usuario paciente NO tiene registro de Paciente asociado")
            
            # Buscar si existe un Paciente con el mismo DNI
            if perfil.dni:
                paciente_existente = Paciente.objects.filter(dni=perfil.dni).first()
                if paciente_existente:
                    print(f"   ✅ SOLUCIÓN: Encontré un Paciente con DNI {perfil.dni}")
                    perfil.paciente = paciente_existente
                    perfil.save()
                    print(f"   ✅ ¡CORREGIDO! Ahora el perfil está asociado al paciente")
                else:
                    print(f"   ❌ No encontré un Paciente con DNI {perfil.dni}")
                    print(f"   💡 Creando nuevo registro de Paciente...")
                    nuevo_paciente = Paciente.objects.create(
                        dni=perfil.dni,
                        nombre=perfil.nombre,
                        apellido=perfil.apellido,
                        genero='O',
                        telefono=perfil.telefono,
                        email=perfil.email
                    )
                    perfil.paciente = nuevo_paciente
                    perfil.save()
                    print(f"   ✅ ¡CORREGIDO! Creé el Paciente y lo asocié al perfil")
        print()
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        print()

print("\n=== FIN ===")
