
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_segura'

carpeta_excel = 'archivos_excel'
usuarios_file = 'usuarios.json'

def cargar_usuarios():
    with open(usuarios_file, 'r') as f:
        return json.load(f)

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
    permisos = session['permisos']
    if permisos != "all" and hoja not in permisos.get(archivo, []):
        return "<h3>No tienes permiso para ver esta hoja.</h3>", 403
    df = pd.read_excel(archivo_path, sheet_name=hoja)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.fillna('')
    formatted_df = df.applymap(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)
    return render_template('tabla.html', nombre=hoja, tabla=formatted_df.to_html(index=False, border=0), archivo=archivo)

@app.route('/descargar/<archivo>/<hoja>')
def descargar_hoja(archivo, hoja):
    archivo_path = os.path.join(carpeta_excel, archivo)
    df = pd.read_excel(archivo_path, sheet_name=hoja)
    output_path = os.path.join("archivos_excel", f"{hoja}.xlsx")
    df.to_excel(output_path, index=False)
    return send_file(output_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
