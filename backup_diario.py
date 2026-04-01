import os
import shutil
from datetime import datetime

# Rutas importantes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')
MEDIA_PATH = os.path.join(BASE_DIR, 'media')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Crear carpeta de backups si no existe
os.makedirs(BACKUP_DIR, exist_ok=True)

# Fecha para el nombre del backup
fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_folder = os.path.join(BACKUP_DIR, f'backup_{fecha}')
os.makedirs(backup_folder, exist_ok=True)

# Copiar base de datos
if os.path.exists(DB_PATH):
    shutil.copy2(DB_PATH, backup_folder)

# Copiar carpeta media
if os.path.exists(MEDIA_PATH):
    shutil.copytree(MEDIA_PATH, os.path.join(backup_folder, 'media'))

print(f'Copia de seguridad realizada en: {backup_folder}')
