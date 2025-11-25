import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.models import InformeInterdisciplinario, Paciente, User

# Buscar usuario agustina
user = User.objects.filter(username='agustina').first()
print(f"Usuario: {user}")

if user:
    try:
        perfil = user.perfil
        print(f"Perfil ROL: {perfil.rol}")
        print(f"Perfil.paciente: {perfil.paciente}")
        
        if perfil.paciente:
            print(f"\nPaciente encontrado: {perfil.paciente.nombre} {perfil.paciente.apellido}")
            
            # Buscar informes
            informes = InformeInterdisciplinario.objects.filter(paciente=perfil.paciente)
            print(f"\nTotal de informes: {informes.count()}")
            
            for informe in informes:
                print(f"\n- Asunto: {informe.asunto}")
                print(f"  Fecha: {informe.fecha_informe}")
                print(f"  Creado: {informe.fecha_creacion}")
                print(f"  Especialistas: {[str(e) for e in informe.especialistas.all()]}")
        else:
            print("El perfil NO tiene paciente asociado")
            
            # Buscar pacientes disponibles
            print("\nPacientes disponibles:")
            for p in Paciente.objects.all():
                print(f"- {p.nombre} {p.apellido} (DNI: {p.dni})")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Usuario no encontrado")
