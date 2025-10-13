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

# === ARCHIVO EXCEL BASE ===
ARCHIVO_EXCEL = r"C:\Users\Diego\mi_app\data\BUENOS AIRES  NOROESTE.xlsx"

def cargar_poligonos():
    """Carga los polígonos desde el Excel."""
    df = pd.read_excel(ARCHIVO_EXCEL)

    # Asegura que existan las columnas esperadas
    columnas = ["NOMBRE", "SUPERFICIE", "PARTIDO", "COLOR HEX", "COORDENADAS"]
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
            "partido": str(fila["PARTIDO"]),
            "color": str(fila["COLOR HEX"]) if pd.notna(fila["COLOR HEX"]) else "#CCCCCC",
            "coords": coords
        })
    return poligonos


def guardar_poligonos(nuevos_datos):
    """Guarda los cambios en el archivo Excel."""
    df = pd.read_excel(ARCHIVO_EXCEL)
    for i, dato in enumerate(nuevos_datos):
        if i < len(df):
            df.at[i, "NOMBRE"] = dato["name"]
            df.at[i, "SUPERFICIE"] = dato["superficie"]
            df.at[i, "PARTIDO"] = dato["partido"]
            df.at[i, "COLOR HEX"] = dato["color"]
    df.to_excel(ARCHIVO_EXCEL, index=False)


# === RUTA DE LOGIN ===
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")  # evita KeyError

        if username in USERS and USERS[username]["password"] == password:
            session["usuario"] = username
            session["rol"] = USERS[username]["rol"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos.")

    return render_template("login.html")


# === RUTA PRINCIPAL ===
@app.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    rol = session["rol"]
    poligonos = cargar_poligonos()

    # Para usuarios no admin, ocultar coordenadas
    if rol != "admin":
        for p in poligonos:
            p["coords"] = []

    return render_template("mapa.html", usuario=usuario, rol=rol, poligonos=poligonos)


# === GUARDAR CAMBIOS (POST) ===
@app.route("/guardar", methods=["POST"])
def guardar():
    if "usuario" not in session:
        return jsonify({"success": False, "message": "No autenticado"})

    datos = request.get_json()
    try:
        guardar_poligonos(datos)
        return jsonify({"success": True})
    except Exception as e:
        print("Error al guardar:", e)
        return jsonify({"success": False})


# === LOGOUT ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
