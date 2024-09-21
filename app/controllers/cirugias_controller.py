# app/controllers/cirugias_controller.py

import datetime
from datetime import datetime
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from flask_jwt_extended import get_jwt_identity
import requests
from app.config import Config

cirugias_bp = Blueprint('cirugias', __name__)

# rutas
ruta_cirugias_get_all = '/cirugias/get/all'
ruta_cirugias_post = '/cirugias/post'

#adicionales
ruta_unidades_get_all = '/unidades/get/all'
ruta_quirofanos_get_all = '/quirofanos/get/all'
ruta_especialidades_get_all = '/especialidades/get/all'
ruta_pacientes_get_all = '/pacientes/get/all' 
ruta_quirofanos_unidades_id = '/quirofanos/unidades/get/id'
ruta_pacientes_get_id = '/pacientes/get/id'
ruta_especialidades_get_all = '/especialidades/get/all'
ruta_finalizaciones_get_all = '/finalizaciones/get/all'
ruta_programaciones_get_all = '/programaciones/get/all'
ruta_complejidades_get_all = '/complejidades/get/all'
ruta_tipos_anestesia_get_all = '/tiposanestesias/get/all'


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
    
        # Crear un diccionario para mapear id_role a role name
        unidades_dict = {unidad['id_unidad']: unidad['unidad'] for unidad in data_unidades}
        quirofanos_dict = {quirofano['id_quirofano']: quirofano['quirofano'] for quirofano in data_quirofanos}
        especialidades_dict = {especialidad['id_especialidad']: especialidad['especialidad'] for especialidad in data_especialidades}
        pacientes_dict = {paciente['id_paciente']: {
            'nombre_completo': f"{paciente['nombre']} {paciente['apellidos']}",
            'doc_numero': paciente['doc_numero']
            } for paciente in data_pacientes}

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
                }
            renamed_cirugias.append(renamed_cirugia)
        data=renamed_cirugias
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de usuarios: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('cirugias_view.html', data=data, headers=headers)


# Ruta para registrar una cirugía
@cirugias_bp.route(ruta_cirugias_post, methods=['GET','POST'])
def cirugias_post():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Registrar Cirugía"
    }
    
    # permisos
    authorized = False
    if ruta_cirugias_post and ruta_unidades_get_all and ruta_quirofanos_unidades_id and ruta_especialidades_get_all and ruta_pacientes_get_id and ruta_complejidades_get_all and ruta_finalizaciones_get_all and ruta_programaciones_get_all and ruta_tipos_anestesia_get_all  in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
    
    api_client = current_app.api_client
    
    try:
        response_unidades = api_client.get_data(ruta_unidades_get_all)
        response_especialidades = api_client.get_data(ruta_especialidades_get_all)
        response_complejidades = api_client.get_data(ruta_complejidades_get_all)
        response_finalizaciones = api_client.get_data(ruta_finalizaciones_get_all)
        response_tipos_anestesias = api_client.get_data(ruta_tipos_anestesia_get_all)
        response_programaciones = api_client.get_data(ruta_programaciones_get_all)
        
        if response_unidades.get('status') == 'success':
            unidades = response_unidades.get('data', [])
        else:
            flash('Error al obtener las unidades', 'error')
            unidades = []
        
        if response_especialidades.get('status') == 'success':
            especialidades = response_especialidades.get('data', [])
        else:
            flash('Error al obtener las especialidades', 'error')
            especialidades = []
        
        if response_complejidades.get('status') == 'success':
            complejidades = response_complejidades.get('data', [])
        else:
            flash('Error al obtener las complejidades', 'error')
            complejidades = []
        
        if response_finalizaciones.get('status') == 'success':
            finalizaciones = response_finalizaciones.get('data', [])
        else:
            flash('Error al obtener las finalizaciones', 'error')
            finalizaciones = []
        
        if response_tipos_anestesias.get('status') == 'success':
            tipos_anestesias = response_tipos_anestesias.get('data', [])
        else:
            flash('Error al obtener los tipos de anestesia', 'error')
            tipos_anestesias = []
        
        if response_programaciones.get('status') == 'success':
            programaciones = response_programaciones.get('data', [])
        else:
            flash('Error al obtener los tipos de programación', 'error')
            programaciones = []
    # Manejo de errores        
    except requests.RequestException as e:
        message = f"Error inesperado al obtener los datos necesarios para registrar una nueva cirugía {str(e)}"
        flash(message, 'warning')
    
    # Crear opciones para el desplegable de unidades y un diccionario para búsqueda rápida
    opciones_unidades = [(unidad['unidad'], unidad['id_unidad']) for unidad in unidades]
    
    # Crear opciones para el desplegable de especialidades y un diccionario para búsqueda rápida
    opciones_especialidades = [(especialidad['especialidad'], especialidad['id_especialidad']) for especialidad in especialidades]
    
    # Crear opciones para el desplegable de complejidades y un diccionario para búsqueda rápida
    opciones_complejidades = [(complejidad['complejidad'], complejidad['id_complejidad']) for complejidad in complejidades]
    
    # Crear opciones para el desplegable de finalizaciones y un diccionario para búsqueda rápida
    opciones_finalizaciones = [(finalizacion['finalizacion'], finalizacion['id_finalizacion']) for finalizacion in finalizaciones]
    
    # Crear opciones para el desplegable de tipos de anestesia y un diccionario para búsqueda rápida
    opciones_tipos_anestesias = [(tipo_anestesia['tipo_anestesia'], tipo_anestesia['id_tipo_anestesia']) for tipo_anestesia in tipos_anestesias]
    
    # Crear opciones para el desplegable de programaciones y un diccionario para búsqueda rápida
    opciones_programaciones = [(programacion['programacion'], programacion['id_programacion']) for programacion in programaciones]
    
    form_data={}
    if request.method == 'POST':
        data = request.form
        id_paciente = request.form.get('id_paciente')
        id_unidad = request.form.get('id_unidad')
        #unidad_data = {}
        paciente_data = {}
        #id_user = get_jwt_identity()
        
        try:
            response_paciente = api_client.post_data(ruta_pacientes_get_id, {'id_paciente':id_paciente})
            if response_paciente['status'] == 'success':
                paciente_data = response_paciente['data']
                print(paciente_data)
            else:
                message = f"Error al obtener los datos del paciente: {response_paciente.get('message', 'Error desconocido')}"
                flash(message, 'warning')
                return redirect(url_for('cirugias.cirugias_get_all'))
            
            try:
                response_quirofanos = api_client.post_data(ruta_quirofanos_unidades_id,{'id_unidad':id_unidad})
                if response_quirofanos and response_quirofanos.get('status')=='success':
                    quirofanos = response_quirofanos.get('data', [])
                    # Validar que el quirófano exista en la lista
                    if data['id_quirofano'] not in [quirofano['id_quirofano'] for quirofano in quirofanos]:
                        flash('El quirófano seleccionado no es válido para la unidad.','error')
                        return redirect(url_for('cirugias.cirugias_post'))
                    else:
                        message = f'Error al obtener los quiórfanos de la unidad: {response_quirofanos.get('message', 'Error desconocido')}'
                        flash(message, 'error')
                        return redirect(url_for('cirugias.cirugias_post'))
            except requests.RequestException as e:
                # Manejo de errores de conexión
                flash(f"Error de conexión al obtener los quirófanos: {str(e)}", 'error')
                return redirect(url_for('cirugias.cirugias_post'))
            except Exception as e:
                # Manejo de otros errores
                flash(f"Error inesperado al obtener los quirófanos: {str(e)}", 'error')
                return redirect(url_for('cirugias.cirugias_post'))
            # response_quirofanos = api_client.post_data(ruta_quirofanos_unidades_id,{'id_unidad':id_unidad})
            # if response_quirofanos['status'] == 'success':
            #     unidad_data = response_quirofanos['data']
            #     print(unidad_data)
            # else:
            #     message = f"Error al obtener los datos de la unidad para el quiórfano: {response_quirofanos.get('message', 'Error desconocido')}"
            #     flash(message, 'warning')
            #     return redirect(url_for('cirugias.cirugias_get_all'))
        except requests.RequestException as e:
            message = f"Error inesperado: {str(e)}"
            flash(message, 'error')
            return redirect(url_for('cirugias.cirugias_get_all'))
        
        programado = form_data.get('programado') == 'si' or form_data.get('programado') == 'true' #si es programado es true(1) si es urgencia es false(0)
        estado = form_data.get('estado') == 'si' or form_data.get('estado') == 'true' #si va con internación es true si es ambulatorio es false
        lista_de_espera = form_data.get('lista_espera') == 'si' or form_data.get('lista_espera') == 'true' #si esta en lista de espera es true si no está es false

        
        form_data['id_paciente']= request.form['id_paciente']
        form_data['fecha_inicio']= request.form['fecha_inicio']
        form_data['hora_inicio'] = request.form['hora_inicio']
        form_data['fecha_fin'] = request.form['fecha_fin']
        form_data['hora_fin'] = request.form['hora_fin']
        form_data['id_unidad'] = request.form['id_unidad']
        form_data['id_quirofano'] = request.form['id_quirofano']
        form_data['id_especialidad'] = request.form['id_especialidad']
        form_data['id_tipo_anestesia_solicitada'] = request.form['id_tipo_anestesia_solicitada']
        form_data['id_tipo_anestesia_realizada'] = request.form['id_tipo_anestesia_realizada']
        form_data['id_programacion'] = request.form['id_programacion']
        form_data['id_complejidad'] = request.form['id_complejidad']
        form_data['comentarios'] = request.form['comentarios']
        form_data['programado'] = programado
        form_data['estado'] = estado
        form_data['lista_de_espera'] = lista_de_espera
       
        try:
            response = api_client.post_data(ruta_cirugias_post, form_data)
            if response.get('status') == 'success':
                flash('Cirugía registrada exitosamente', 'success')
                return redirect(url_for('cirugias.cirugias_get_all'))
            else:
                error_message = response.get('message', 'Error desconocido al registrar la cirugía.')
                flash(error_message, 'warning')
                return render_template('cirugias_form.html', headers=headers, form_action=url_for('cirugias.cirugias_post'), form_method='POST', form_data=form_data, opciones_complejidades=opciones_complejidades, opciones_especialidades=opciones_especialidades, opciones_finalizaciones=opciones_finalizaciones,opciones_programaciones=opciones_programaciones, opciones_tipos_anestesias=opciones_tipos_anestesias,opciones_unidades=opciones_unidades)
        except Exception as e:
            flash('Error inesperado al registrar la cirugía: ' + str(e), 'warning')

    return render_template('cirugias_form.html', headers=headers, form_action=url_for('cirugias.cirugias_post'), form_method='POST', form_data=form_data, opciones_complejidades=opciones_complejidades, opciones_especialidades=opciones_especialidades, opciones_finalizaciones=opciones_finalizaciones,opciones_programaciones=opciones_programaciones, opciones_tipos_anestesias=opciones_tipos_anestesias,opciones_unidades=opciones_unidades)
        
            
            
        
                