import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE app_entrevista ADD COLUMN estado VARCHAR(20) DEFAULT "pendiente"')
    print('Campo estado agregado')
except Exception as e:
    print(f'Error al agregar estado: {e}')

try:
    cursor.execute('ALTER TABLE app_entrevista ADD COLUMN especialista_asignado_id INTEGER')
    print('Campo especialista_asignado_id agregado')
except Exception as e:
    print(f'Error al agregar especialista_asignado_id: {e}')

try:
    cursor.execute('ALTER TABLE app_entrevista ADD COLUMN fecha_creacion DATETIME')
    print('Campo fecha_creacion agregado')
except Exception as e:
    print(f'Error al agregar fecha_creacion: {e}')

try:
    cursor.execute('ALTER TABLE app_entrevista ADD COLUMN observaciones TEXT DEFAULT ""')
    print('Campo observaciones agregado')
except Exception as e:
    print(f'Error al agregar observaciones: {e}')

conn.commit()
conn.close()
print('¡Todos los campos procesados!')
