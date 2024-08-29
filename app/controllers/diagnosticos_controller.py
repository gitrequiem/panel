# app/controllers/diagnosticos_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

diagnosticos_bp = Blueprint('diagnosticos', __name__)

# rutas
ruta_diagnosticos_get_all = '/diagnosticos/get/all'
ruta_diagnosticos_post = '/diagnosticos/post'

#adicionales
ruta_especialidades_get_all = '/especialidades/get/all'

@diagnosticos_bp.route(ruta_diagnosticos_get_all, methods=['GET'])
def diagnosticos_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Diagnósticos"
    }
    
    
    authorized = False
    if ruta_diagnosticos_get_all and ruta_especialidades_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de usuarios y roles de la API
        response_diagnosticos = api_client.get_data(ruta_diagnosticos_get_all)
        response_especialidades = api_client.get_data(ruta_especialidades_get_all)

        if response_diagnosticos['status'] == 'success':
            data_diagnosticos = response_diagnosticos['data']  # Extrae la lista de diagnosticos
            message = f"{session['username']}: listado de diagnósticos obtenido!"
        else:
            message = f"Error en la respuesta de la API (diagnósticos): {response_diagnosticos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_diagnosticos = []  # Asegúrate de pasar una lista vacía en caso de error

        if response_especialidades['status'] == 'success':
            data_especialidades = response_especialidades['data']  # Extrae la lista de especialidades
            message += f" y diagnósticos obtenidos!"
        else:
            message += f"Error en la respuesta de la API (especialidades): {response_especialidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_especialidades = []  # Asegúrate de pasar una lista vacía en caso de error

        # Crear un diccionario para mapear id_especialidad a especialidad
        especialidades_dict = {especialidad['id_especialidad']: especialidad['especialidad'] for especialidad in data_especialidades}

        # Agregar el nombre de la especialidad a cada diagnóstico y renombrar las claves
        renamed_diagnosticos = []
        for diagnostico in data_diagnosticos:
            diagnostico['especialidad'] = especialidades_dict.get(diagnostico['id_especialidad'], "Desconocido")  # Si no se encuentra el id_role
            renamed_diagnostico = {
                "ID": diagnostico['id_diagnostico'],
                "Diagnóstico": diagnostico['diagnostico'],
                # "Email": user['email'],
                # "Documento": user['usernumdoc'],
                "Especialidad": diagnostico['especialidad'],
                # "Bloqueado": user['is_blocked'],
                # "Fecha de Bloqueo": user['blocked_at'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_diagnosticos.append(renamed_diagnostico)

        data = renamed_diagnosticos
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de diagnósticos: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('diagnosticos_view.html', data=data, headers=headers)

# Ruta para crear un diagnóstico
@diagnosticos_bp.route(ruta_diagnosticos_post, methods=['GET','POST'])
def diagnosticos_post():
    message = ''

    headers = {
        "app": Config.APP_TITLE,
        "section": "Crear Diagnóstico"
    }

    authorized = ruta_diagnosticos_post and ruta_especialidades_get_all in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para crear un diagnóstico (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))
    api_client = current_app.api_client

    try:
        response = api_client.get_data(ruta_especialidades_get_all) # accede a la ruta del get all de especialidades de la api
        if response.get('status') == 'success':
            especialidades = response.get('data', [])
        else:
            flash('Error al obtener las especialidades', 'error')
            especialidades = []
    except Exception as e:
        flash('Error inesperado al obtener las especialidades', 'error')
        especialidades = []

    # Crear opciones para el desplegable de especialidades y un diccionario para búsqueda rápida
    opciones_especialidades = [(especialidad['especialidad'], especialidad['id_especialidad']) for especialidad in especialidades]
    
    print(opciones_especialidades) # imprime por consola las especialidades para asegurarme que funciona.

    form_data = {
        'diagnostico': ''
        
    }

    if request.method == 'POST':
        # Obtener datos del formulario
        form_data['diagnostico'] = request.form['diagnostico']
        especialidad_seleccionada = request.form['especialidad']  # Nombre o ID de la especialidad seleccionada
        
        try:
            especialidad_seleccionada = int(especialidad_seleccionada) # para que tome el id en vez del string
        except ValueError:
            flash("La especialidad seleccionada no es válida.", "error")
            return render_template('diagnosticos_form.html', headers=headers, form_action=url_for('diagnosticos.diagnosticos_post'), form_method='POST', form_data=form_data, opciones_especialidades=opciones_especialidades)

        # Crear el JSON para enviar a la API
        data = {
            'diagnostico': form_data['diagnostico'],
            'id_especialidad': especialidad_seleccionada
        }

        # Enviar datos a la API para crear el nuevo diagnóstico
        try:
            response = api_client.post_data(ruta_diagnosticos_post, data)
            if response.get('status') == 'success':
                flash('Diagnóstico creado exitosamente', 'success')
                return redirect(url_for('diagnosticos.diagnosticos_get_all'))
            else:
                error_message = response.get('message', 'Error desconocido al crear el diagnóstico.')
                flash(error_message, 'warning')
                return render_template('diagnosticos_form.html', headers=headers, form_action=url_for('diagnosticos.diagnosticos_post'), form_method='POST', form_data=form_data, opciones_especialidades=opciones_especialidades)
        except Exception as e:
            flash('Error inesperado al crear el diagnóstico: ' + str(e), 'warning')

    return render_template('diagnosticos_form.html', headers=headers, form_action=url_for('diagnosticos.diagnosticos_post'), form_method='POST', form_data=form_data, opciones_especialidades=opciones_especialidades)