# app/controllers/pacientes_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

pacientes_bp = Blueprint('pacientes', __name__)

# Ruta
ruta_pacientes_get_all = '/pacientes/get/all'

# Rutas adicionales
ruta_doctipos_get_all = '/doctipos/get/all'
ruta_localidades_get_all = '/localidades/get/all'
ruta_provincias_get_all = '/provincias/get/all'
ruta_nacionalidades_get_all = '/nacionalidades/get/all'

@pacientes_bp.route(ruta_pacientes_get_all, methods=['GET'])
def pacientes_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Pacientes"
    }
  
    authorized = False
    if ruta_pacientes_get_all and ruta_doctipos_get_all and ruta_localidades_get_all and ruta_provincias_get_all and ruta_nacionalidades_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de la API
        response_pacientes = api_client.get_data(ruta_pacientes_get_all)
        response_doctipos = api_client.get_data(ruta_doctipos_get_all)
        response_provincias = api_client.get_data(ruta_provincias_get_all)
        response_localidades = api_client.get_data(ruta_localidades_get_all)
        response_nacionalidades = api_client.get_data(ruta_nacionalidades_get_all)

        if response_pacientes['status'] == 'success':
            data_pacientes = response_pacientes['data']  # Extrae la lista 
            message = f"{session['username']}: listado de pacientes obtenido!"
        else:
            message = f"Error en la respuesta de la API (pacientes): {response_pacientes.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_pacientes = []  # Asegúrate de pasar una lista vacía en caso de error

        if response_doctipos['status'] == 'success':
            data_doctipos = response_doctipos['data']  # Extrae la lista 
            message += f" y tipos de documento obtenidos!"
        else:
            message += f"Error en la respuesta de la API (doctipos): {response_doctipos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_doctipos = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_localidades['status'] == 'success':
            data_localidades = response_localidades['data']  # Extrae la lista 
            message += f" y localidades obtenidos!"
        else:
            message += f"Error en la respuesta de la API (localidades): {response_localidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_localidades = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_nacionalidades['status'] == 'success':
            data_nacionalidades = response_nacionalidades['data']  # Extrae la lista 
            message += f" y nacionalidades obtenidos!"
        else:
            message += f"Error en la respuesta de la API (nacionalidades): {response_nacionalidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_nacionalidades = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_provincias['status'] == 'success':
            data_provincias = response_provincias['data']  # Extrae la lista 
            message += f" y provincias obtenidos!"
        else:
            message += f"Error en la respuesta de la API (provincias): {response_provincias.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_provincias = []  # Asegúrate de pasar una lista vacía en caso de error

        # Crear un diccionario para mapear las entidades dependientes
        doctipos_dict = {doctipo['id_doc_tipo']: doctipo['doc_tipo'] for doctipo in data_doctipos}
        localidades_dict = {}
        for localidad in data_localidades:
            id_provincia = localidad.get('id_provincia')
        if id_provincia:
            localidades_dict.setdefault(id_provincia, {})[localidad['id_localidad']] = localidad['localidad']
       
        provincias_dict = {provincia['id_provincia']: provincia['provincia'] for provincia in data_provincias}
        nacionalidades_dict = {nacionalidad['id_nacionalidad']: nacionalidad['nacionalidad'] for nacionalidad in data_nacionalidades}

        # Agregar el nombre y renombrar las claves
        renamed_pacientes = []
        for paciente in data_pacientes:
            
            paciente['doctipos'] = doctipos_dict.get(paciente['id_doc_tipo'], "Desconocido")  # Si no se encuentra el id
            provincia_id = paciente.get('id_provincia')
            localidad_id = paciente.get('id_localidad')
            if provincia_id:
                paciente['localidades'] = localidades_dict.get(provincia_id, {}).get(localidad_id, "Desconocido")
                paciente['provincias'] = provincias_dict.get(provincia_id, "Provincia desconocida")
            else:
                paciente['localidades'] = "Provincia desconocida"
                paciente['provincias'] = "Provincia desconocida"
         
            paciente['nacionalidades'] = nacionalidades_dict.get(paciente['id_nacionalidad'], "Desconocido")  # Si no se encuentra el id
            renamed_paciente = {
                "ID": paciente['id_paciente'],
                "Nombre": paciente['nombre'],
                "Apellidos": paciente['apellidos'],
                "Tipo de Doc.": paciente['doc_tipo'],
                "Número de Doc.": paciente['doc_numero'],
                "Localidad": paciente['localidad'],
                "Nacionalidad": paciente['nacionalidad'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_pacientes.append(renamed_paciente)

        data = renamed_pacientes
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de pacientes: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('pacientes_view.html', data=data, headers=headers)




 
