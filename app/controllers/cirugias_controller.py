# app/controllers/cirugias_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
import requests
from app.config import Config

cirugias_bp = Blueprint('cirugias', __name__)

# rutas
ruta_cirugias_get_all = '/cirugias/get/all'

#adicionales
ruta_unidades_get_all = '/unidades/get/all'
ruta_quirofanos_get_all = '/quirofanos/get/all'
ruta_especialidades_get_all = '/especialidades/get/all'
ruta_pacientes_get_all = '/pacientes/get/all' 
# ruta_nacionalidades_get_all = '/nacionalidades/get/all'
# ruta_localidades_get_all = '/localidades/get/all'

# ruta para traer los datos especificados
@cirugias_bp.route(ruta_cirugias_get_all, methods=['GET'])
def cirugias_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Cirugías"
    }
    
    # permisos
    authorized = False
    if ruta_cirugias_get_all and ruta_unidades_get_all and ruta_quirofanos_get_all and ruta_especialidades_get_all and ruta_pacientes_get_all  in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
    
    # instancia api_client    
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de usuarios y roles de la API
        response_cirugias = api_client.get_data(ruta_cirugias_get_all)        # principal
        response_unidades = api_client.get_data(ruta_unidades_get_all)   # rutas adicionales
        response_quirofanos = api_client.get_data(ruta_quirofanos_get_all)   # rutas adicionales
        response_especialidades = api_client.get_data(ruta_especialidades_get_all)   # rutas adicionales
        response_pacientes = api_client.get_data(ruta_pacientes_get_all)   # rutas adicionales
        # response_nacionalidades = api_client.get_data(ruta_nacionalidades_get_all)   # rutas adicionales
        # response_localidades = api_client.get_data(ruta_localidades_get_all)   # rutas adicionales

        # obtener rta de la api para la consulta principal
        if response_cirugias['status'] == 'success':
            data_cirugias = response_cirugias['data']  # Extrae la lista de usuarios
            message = f"{session['username']}: listado de cirugías obtenido!"
        else:
            message = f"Error en la respuesta de la API (cirugias): {response_cirugias.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_cirugias = []  # Asegúrate de pasar una lista vacía en caso de error

        # obtener rta de la api para la consulta adicional
        if response_unidades['status'] == 'success':
            data_unidades = response_unidades['data']  # Extrae la lista 
            message += f" y unidades obtenidos!"
        else:
            message += f"Error en la respuesta de la API (unidades): {response_unidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_unidades = []  # Asegúrate de pasar una lista vacía en caso de error
            
        if response_quirofanos['status'] == 'success':
            data_quirofanos = response_quirofanos['data']  # Extrae la lista 
            message += f" y quirófanos obtenidos!"
        else:
            message += f"Error en la respuesta de la API (quirófanos): {response_quirofanos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_quirofanos = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_especialidades['status'] == 'success':
            data_especialidades = response_especialidades['data']  # Extrae la lista 
            message += f" y especialidades obtenidos!"
        else:
            message += f"Error en la respuesta de la API (especialidades): {response_especialidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_especialidades = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_pacientes['status'] == 'success':
            data_pacientes = response_pacientes['data']  # Extrae la lista 
            message += f" y pacientes obtenidos!"
        else:
            message += f"Error en la respuesta de la API (pacientes): {response_pacientes.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_pacientes = []  # Asegúrate de pasar una lista vacía en caso de error
        
        # if response_nacionalidades['status'] == 'success':
        #     data_nacionalidades = response_nacionalidades['data']  # Extrae la lista 
        #     message += f" y nacionalidades obtenidos!"
        # else:
        #     message += f"Error en la respuesta de la API (nacionalidades): {response_nacionalidades.get('message', 'Error desconocido')}"
        #     flash(message, 'danger')
        #     data_nacionalidades = []  # Asegúrate de pasar una lista vacía en caso de error
        
        # if response_localidades['status'] == 'success':
        #     data_localidades = response_localidades['data']  # Extrae la lista 
        #     message += f" y localidades obtenidos!"
        # else:
        #     message += f"Error en la respuesta de la API (localidades): {response_localidades.get('message', 'Error desconocido')}"
        #     flash(message, 'danger')
        #     data_localidades = []  # Asegúrate de pasar una lista vacía en caso de error


        # Crear un diccionario para mapear id_role a role name
        unidades_dict = {unidad['id_unidad']: unidad['unidad'] for unidad in data_unidades}
        quirofanos_dict = {quirofano['id_quirofano']: quirofano['quirofano'] for quirofano in data_quirofanos}
        especialidades_dict = {especialidad['id_especialidad']: especialidad['especialidad'] for especialidad in data_especialidades}
        pacientes_dict = {paciente['id_paciente']: {
            'nombre_completo': f"{paciente['nombre']} {paciente['apellidos']}",
            'doc_numero': paciente['doc_numero']
            } for paciente in data_pacientes}
        # nacionalidades_dict = {nacionalidad['id_nacionalidad']: nacionalidad['nacionalidad'] for nacionalidad in data_nacionalidades}
        # localidades_dict = {localidad['id_localidad']: localidad['localidad'] for localidad in data_localidades}

        # Agregar el nombre del rol a cada usuario y renombrar las claves
        renamed_cirugias = []
        for cirugia in data_cirugias:
            data_pacientes = pacientes_dict.get(cirugia['id_paciente'], {})
            #paciente_id = cirugia['id_paciente']
            #paciente_localidad_id = data_pacientes.get('id_localidad')
            cirugia['unidad'] = unidades_dict.get(cirugia['id_unidad'], "")
            cirugia['quirofano'] = quirofanos_dict.get(cirugia['id_quirofano'])
            cirugia['especialidad'] = especialidades_dict.get(cirugia['id_especialidad'])
            # localidad_data = localidades_dict.get(paciente_localidad_id, {})
            renamed_cirugia = {
                "ID Cirugía": cirugia['id_cirugia'],
                "Fecha y Hora Inicio": f"{cirugia['fecha_inicio']} {cirugia['hora_inicio']}",
                #"Fecha y Hora Fin": f"{cirugia['fecha_fin']} {cirugia['hora_fin']}",
                "Unidad": cirugia['unidad'],
                "Quirófano": cirugia['quirofano'],
                "Especialidad": cirugia['especialidad'],
                "Programado/URG": "Prog." if cirugia['programado'] else "URG",
                "Paciente": f"{data_pacientes.get('nombre_completo', 'Paciente no encontrado')}",
                "Número de Documento": data_pacientes.get('doc_numero', 'Documento no encontrado'),
                "Acciones": f'<a href="#" class="btn btn-primary">Ver más</a>' '&nbsp;'  
                            f'<a href="#" class="btn btn-primary">Editar</a>'
                # "Nacionalidad": nacionalidades_dict.get(paciente_id, "Desconocido"),  
                # "Localidad": localidad_data.get('localidad', 'Desconocida'),  
                }
            renamed_cirugias.append(renamed_cirugia)
        data=renamed_cirugias
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de usuarios: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('cirugias_view.html', data=data, headers=headers)