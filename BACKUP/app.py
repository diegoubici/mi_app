import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "BanfiClaveSegura123"

# === CONFIGURACIÓN DE USUARIOS ===
USERS = {
    "DSUBICI": {"password": "Banfi138", "rol": "admin"},
    "usuario1": {"password": "contraseña1", "rol": "usuario"},
    "usuario2": {"password": "contraseña2", "rol": "usuario"},
    "usuario3": {"password": "contraseña3", "rol": "usuario"},
    "usuario4": {"password": "contraseña4", "rol": "usuario"},
    "usuario5": {"password": "contraseña5", "rol": "usuario"}
}

# === CARPETAS BASE ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_DIR = os.path.join(DATA_DIR, "usuarios")
ORIGINAL_FILE = os.path.join(DATA_DIR, "BUENOS AIRES  NOROESTE.xlsx")

os.makedirs(USERS_DIR, exist_ok=True)
for u in USERS:
    os.makedirs(os.path.join(USERS_DIR, u), exist_ok=True)

# === FUNCIONES ===
def obtener_archivos_usuario(usuario):
    carpeta = os.path.join(USERS_DIR, usuario)
    return sorted([f for f in os.listdir(carpeta) if f.endswith(".xlsx")])

def obtener_ruta_archivo(usuario, archivo):
    return os.path.join(USERS_DIR, usuario, archivo)

def cargar_poligonos(ruta_archivo):
    df = pd.read_excel(ruta_archivo)
    columnas = ["NOMBRE", "SUPERFICIE", "PARTIDO", "STATUS", "COLOR HEX", "COORDENADAS"]
    for col in columnas:
        if col not in df.columns:
            df[col] = ""

    poligonos = []
    for _, fila in df.iterrows():
        coords = []
        if pd.notna(fila["COORDENADAS"]):
            try:
                puntos = str(fila["COORDENADAS"]).split(" ")
                for p in puntos:
                    lon, lat = map(float, p.split(","))
                    coords.append([lat, lon])
            except Exception:
                coords = []
        poligonos.append({
            "name": str(fila["NOMBRE"]),
            "superficie": str(fila["SUPERFICIE"]),
            "status": str(fila["STATUS"]),
            "partido": str(fila["PARTIDO"]),
            "color": str(fila["COLOR HEX"]) if pd.notna(fila["COLOR HEX"]) else "#CCCCCC",
            "coords": coords
        })
    return poligonos

def guardar_poligonos(ruta_archivo, nuevos_datos):
    df = pd.read_excel(ruta_archivo)
    for dato in nuevos_datos:
        idx = dato.get("index")
        if idx is not None and 0 <= idx < len(df):
            df.at[idx, "NOMBRE"] = dato["name"]
            df.at[idx, "SUPERFICIE"] = dato["superficie"]
            df.at[idx, "STATUS"] = dato["status"]
            df.at[idx, "PARTIDO"] = dato["partido"]
            df.at[idx, "COLOR HEX"] = dato["color"]
    df.to_excel(ruta_archivo, index=False)

# === LOGIN ===
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username]["password"] == password:
            session["usuario"] = username
            session["rol"] = USERS[username]["rol"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos.")
    return render_template("login.html")

# === LOGOUT ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# === SELECCIÓN DE ARCHIVO ===
@app.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    rol = session["rol"]

    archivo_seleccionado = session.get("archivo_seleccionado")
    if not archivo_seleccionado:
        archivos_usuario = obtener_archivos_usuario(usuario)
        return render_template("seleccionar_archivo.html", archivos=archivos_usuario, usuario=usuario, rol=rol)

    ruta_archivo = obtener_ruta_archivo(usuario, archivo_seleccionado)
    poligonos = cargar_poligonos(ruta_archivo)
    return render_template("mapa.html", usuario=usuario, rol=rol, poligonos=poligonos)

@app.route("/abrir/<nombre>")
def abrir_archivo(nombre):
    if "usuario" not in session:
        return redirect(url_for("login"))
    session["archivo_seleccionado"] = nombre
    return redirect(url_for("index"))

@app.route("/nuevo_archivo", methods=["POST"])
def nuevo_archivo():
    if "usuario" not in session:
        return jsonify({"success": False, "message": "No autenticado"})

    usuario = session["usuario"]
    nombre = request.form.get("nombre")
    if not nombre.endswith(".xlsx"):
        nombre += ".xlsx"

    ruta = obtener_ruta_archivo(usuario, nombre)
    if os.path.exists(ruta):
        return jsonify({"success": False, "message": "El archivo ya existe."})

    df = pd.read_excel(ORIGINAL_FILE)
    df.to_excel(ruta, index=False)
    return jsonify({"success": True, "archivo": nombre})

# === GUARDAR CAMBIOS ===
@app.route("/guardar", methods=["POST"])
def guardar():
    if "usuario" not in session:
        return jsonify({"success": False, "message": "No autenticado"})

    archivo_seleccionado = session.get("archivo_seleccionado")
    if not archivo_seleccionado:
        return jsonify({"success": False, "message": "No hay archivo seleccionado."})

    ruta_archivo = obtener_ruta_archivo(session["usuario"], archivo_seleccionado)
    datos = request.get_json()
    try:
        guardar_poligonos(ruta_archivo, datos)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
