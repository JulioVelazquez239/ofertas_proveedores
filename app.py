from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_segura'

carpeta_excel = 'archivos_excel'
usuarios_file = 'usuarios.json'

def cargar_usuarios():
    if not os.path.exists(usuarios_file):
        return {}
    with open(usuarios_file, 'r') as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open(usuarios_file, 'w') as f:
        json.dump(usuarios, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def login():
    usuarios = cargar_usuarios()
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user in usuarios and usuarios[user]['password'] == pwd:
            session['user'] = user
            session['permisos'] = usuarios[user]['permisos']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    archivos = os.listdir(carpeta_excel)
    return render_template('dashboard.html', archivos=archivos)

@app.route('/archivo/<archivo>')
def ver_archivo(archivo):
    if 'user' not in session:
        return redirect(url_for('login'))
    archivo_path = os.path.join(carpeta_excel, archivo)
    if not os.path.exists(archivo_path):
        return "<h3>Archivo no encontrado</h3>", 404
    xls = pd.ExcelFile(archivo_path)
    hojas = xls.sheet_names
    permisos = session['permisos']
    if permisos == "all":
        hojas_autorizadas = hojas
    else:
        hojas_autorizadas = permisos.get(archivo, [])
    hojas_filtradas = [hoja for hoja in hojas if hoja in hojas_autorizadas]
    return render_template('archivo.html', archivo=archivo, hojas=hojas_filtradas)

@app.route('/archivo/<archivo>/hoja/<hoja>')
def mostrar_hoja(archivo, hoja):
    if 'user' not in session:
        return redirect(url_for('login'))
    archivo_path = os.path.join(carpeta_excel, archivo)
    if not os.path.exists(archivo_path):
        return "<h3>Archivo no encontrado</h3>", 404
    permisos = session['permisos']
    if permisos != "all" and hoja not in permisos.get(archivo, []):
        return "<h3>No tienes permiso para ver esta hoja.</h3>", 403
    df = pd.read_excel(archivo_path, sheet_name=hoja, header=None)
    max_cols = max(df.apply(lambda row: row.last_valid_index() if row.last_valid_index() else 0, axis=1).fillna(0).astype(int)) + 1
    df = df.iloc[:, :max_cols].fillna("")
    return render_template('tabla_excel_like.html', nombre=hoja, tabla=df.to_html(index=False, header=False, border=0, classes="table table-striped"))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
