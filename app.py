from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# Lista de opciones para el número de máquinas
NUMERO_MAQUINAS = [f"skitrm {i}" for i in range(1, 55)]  # Del skitrm 1 al skitrm 54

# Función para cargar registros
def cargar_registros():
    if os.path.exists('registros.json'):
        with open('registros.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Función para cargar clientes
def cargar_clientes():
    if os.path.exists('clientes.json'):
        with open('clientes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Función para cargar proyectos
def cargar_proyectos():
    if os.path.exists('proyectos.json'):
        with open('proyectos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Función para guardar clientes
def guardar_clientes(clientes):
    with open('clientes.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(list(set(clientes))), f, ensure_ascii=False, indent=4)

# Función para guardar proyectos
def guardar_proyectos(proyectos):
    with open('proyectos.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(list(set(proyectos))), f, ensure_ascii=False, indent=4)

# Función para guardar registros
def guardar_registros(registros):
    with open('registros.json', 'w', encoding='utf-8') as f:
        json.dump(registros, f, ensure_ascii=False, indent=4)

def cliente_en_uso(cliente):
    registros = cargar_registros()
    return any(r['cliente'] == cliente for r in registros)

@app.route('/', methods=['GET', 'POST'])
def index():
    registros = cargar_registros()
    clientes = cargar_clientes()
    proyectos = cargar_proyectos()
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nuevo_cliente = request.form['cliente']
        nuevo_proyecto = request.form['proyecto']
        nuevo_registro = {
            'cliente': nuevo_cliente,
            'proyecto': nuevo_proyecto,
            'num_maquinas': request.form['num_maquinas'],
            'tipo': request.form['tipo'],
            'observaciones': request.form.get('observaciones', '')  # Campo opcional
        }
        
        # Buscar si existe un registro igual
        registro_existente = None
        for i, registro in enumerate(registros):
            if (registro['cliente'] == nuevo_cliente and 
                registro['proyecto'] == nuevo_proyecto and
                registro['num_maquinas'] == nuevo_registro['num_maquinas'] and
                registro['tipo'] == nuevo_registro['tipo']):
                registro_existente = i
                break
        
        if registro_existente is not None:
            # Actualizar registro existente solo si es exactamente igual
            registros[registro_existente] = nuevo_registro
        else:
            # Agregar nuevo registro
            registros.append(nuevo_registro)
        
        # Agregar el nuevo cliente si no existe en la lista
        if nuevo_cliente not in clientes:
            clientes.append(nuevo_cliente)
            guardar_clientes(clientes)
        
        # Agregar el nuevo proyecto si no existe en la lista
        if nuevo_proyecto not in proyectos:
            proyectos.append(nuevo_proyecto)
            guardar_proyectos(proyectos)
        
        # Guardar todos los registros
        guardar_registros(registros)
        
        return redirect(url_for('index'))
    
    return render_template('index.html', 
                         numero_maquinas=NUMERO_MAQUINAS,
                         registros=registros,
                         clientes=sorted(clientes),
                         proyectos=sorted(proyectos))

@app.route('/eliminar/<cliente>/<proyecto>')
def eliminar_registro(cliente, proyecto):
    registros = cargar_registros()
    
    # Buscar y eliminar el registro
    registros = [r for r in registros if not (r['cliente'] == cliente and r['proyecto'] == proyecto)]
    
    # Guardar los registros actualizados
    guardar_registros(registros)
    
    return redirect(url_for('index'))

@app.route('/eliminar_cliente/<cliente>')
def eliminar_cliente(cliente):
    if cliente_en_uso(cliente):
        return redirect(url_for('index'))  # No eliminamos si está en uso
        
    clientes = cargar_clientes()
    if cliente in clientes:
        clientes.remove(cliente)
        guardar_clientes(clientes)
    
    return redirect(url_for('index'))

@app.route('/actualizar_observaciones/<cliente>/<proyecto>', methods=['POST'])
def actualizar_observaciones(cliente, proyecto):
    registros = cargar_registros()
    
    # Buscar el registro específico
    for registro in registros:
        if registro['cliente'] == cliente and registro['proyecto'] == proyecto:
            # Actualizar las observaciones
            data = request.get_json()
            registro['observaciones'] = data.get('observaciones', '')
            break
    
    # Guardar los cambios
    guardar_registros(registros)
    
    return jsonify({'observaciones': registro['observaciones']})

if __name__ == '__main__':
    app.run(debug=True) 