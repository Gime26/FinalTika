import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.models import Detallepagos, Paciente, User

# Ver comprobantes
print("=== COMPROBANTES EN LA BASE DE DATOS ===")
print(f"Total comprobantes: {Detallepagos.objects.count()}\n")

for c in Detallepagos.objects.all():
    print(f"Código: {c.codigo_pago}")
    print(f"Monto: ${c.monto}")
    print(f"Observaciones: {c.observaciones}")
    print("-" * 50)

# Ver estructura del modelo
print("\n=== CAMPOS DEL MODELO Detallepagos ===")
for field in Detallepagos._meta.get_fields():
    print(f"- {field.name}: {field.__class__.__name__}")
