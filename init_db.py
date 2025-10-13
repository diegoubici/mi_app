import sqlite3

# Conectamos (si no existe el archivo, lo crea)
conn = sqlite3.connect("datos.sqlite")
cur = conn.cursor()

# Creamos una tabla de ejemplo con algunos polígonos
cur.execute("""
CREATE TABLE IF NOT EXISTS poligonos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    categoria TEXT,
    color TEXT,
    geom TEXT
)
""")

# Insertamos algunos polígonos de ejemplo
cur.execute("INSERT INTO poligonos (nombre, categoria, color, geom) VALUES (?,?,?,?)",
            ("Lote 1", "Agricola", "#FF0000", "POLYGON((-63.84 -35.04, -63.85 -35.04, -63.85 -35.03, -63.84 -35.03, -63.84 -35.04))"))

cur.execute("INSERT INTO poligonos (nombre, categoria, color, geom) VALUES (?,?,?,?)",
            ("Lote 2", "Ganadero", "#0000FF", "POLYGON((-63.83 -35.05, -63.84 -35.05, -63.84 -35.04, -63.83 -35.04, -63.83 -35.05))"))

conn.commit()
conn.close()

print("✅ Base de datos creada: datos.sqlite")
