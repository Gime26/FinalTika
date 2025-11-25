import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
result = cursor.execute('PRAGMA table_info(app_entrevista)')
print("Estructura de app_entrevista:")
for row in result:
    print(row)
conn.close()
