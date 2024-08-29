# app/controllers/intervenciones_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

intervenciones_bp = Blueprint('intervenciones', __name__)

# rutas
ruta_intervenciones_get_all = '/intervenciones/get/all'
ruta_intervenciones_post = '/intervenciones/post'

#adicionales
ruta_diagnosticos_get_all = '/diagnosticos/get/all'



@intervenciones_bp.route(ruta_intervenciones_get_all, methods=['GET'])
def intervenciones_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Intervenciones"
    }
    
    authorized = False
    if ruta_intervenciones_get_all and ruta_diagnosticos_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de usuarios y roles de la API
        response_intervenciones = api_client.get_data(ruta_intervenciones_get_all)
        response_diagnosticos = api_client.get_data(ruta_diagnosticos_get_all)

        if response_intervenciones['status'] == 'success':
            data_intervenciones = response_intervenciones['data']  # Extrae la lista 
            message = f"{session['username']}: listado de intervenciones obtenido!"
        else:
            message = f"Error en la respuesta de la API (intervenciones): {response_intervenciones.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_intervenciones = []  # Asegúrate de pasar una lista vacía en caso de error

        if response_diagnosticos['status'] == 'success':
            data_diagnosticos = response_diagnosticos['data']  # Extrae la lista 
            message += f" e intervenciones obtenidos!"
        else:
            message += f"Error en la respuesta de la API (diagnosticos): {response_diagnosticos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_diagnosticos = []  # Asegúrate de pasar una lista vacía en caso de error

        # Crear un diccionario para mapear 
        diagnosticos_dict = {diagnostico['id_diagnostico']: diagnostico['diagnostico'] for diagnostico in data_diagnosticos}

        # Agregar el nombre y renombrar las claves
        renamed_intervenciones = []
        for intervencion in data_intervenciones:
            intervencion['diagnostico'] = diagnosticos_dict.get(intervencion['id_diagnostico'], "Desconocido")  # Si no se encuentra el id
            renamed_intervencion = {
                "ID": intervencion['id_intervencion'],
                "Intervención": intervencion['intervencion'],
                "Diagnóstico": intervencion['diagnostico'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_intervenciones.append(renamed_intervencion)

        data = renamed_intervenciones
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de intervenciones: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('intervenciones_view.html', data=data, headers=headers)

# Ruta para crear una intervención
@intervenciones_bp.route(ruta_intervenciones_post, methods=['GET','POST'])
def intervenciones_post():
    message = ''

    headers = {
        "app": Config.APP_TITLE,
        "section": "Crear Intervención"
    }

    authorized = ruta_intervenciones_post and ruta_diagnosticos_get_all in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para crear una intervención (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))
    api_client = current_app.api_client

    try:
        response = api_client.get_data(ruta_diagnosticos_get_all) # accede a la ruta del get all de diagnósticos de la api
        if response.get('status') == 'success':
            diagnosticos = response.get('data', [])
        else:
            flash('Error al obtener los diagnósticos', 'error')
            diagnosticos = []
    except Exception as e:
        flash('Error inesperado al obtener los diagnósticos', 'error')
        diagnosticos = []

    # Crear opciones para el desplegable de diagnósticos y un diccionario para búsqueda rápida
    opciones_diagnosticos = [(diagnostico['diagnostico'], diagnostico['id_diagnostico']) for diagnostico in diagnosticos]
    
    print(opciones_diagnosticos) # imprime por consola los diagnósticos para asegurarme que funciona.

    form_data = {
        'intervencion': ''
        
    }

    if request.method == 'POST':
        # Obtener datos del formulario
        form_data['intervencion'] = request.form['intervencion']
        diagnostico_seleccionado = request.form['diagnostico']  # Nombre o ID del diagnóstico seleccionado
        
        try:
            diagnostico_seleccionado = int(diagnostico_seleccionado) # para que tome el id en vez del string
        except ValueError:
            flash("El diagnóstico seleccionado no es válido.", "error")
            return render_template('intervenciones_form.html', headers=headers, form_action=url_for('intervenciones.intervenciones_post'), form_method='POST', form_data=form_data, opciones_diagnosticos=opciones_diagnosticos)

        # Crear el JSON para enviar a la API
        data = {
            'intervencion': form_data['intervencion'],
            'id_diagnostico': diagnostico_seleccionado
        }

        # Enviar datos a la API para crear la nueva intervención
        try:
            response = api_client.post_data(ruta_intervenciones_post, data)
            if response.get('status') == 'success':
                flash('Intervención creada exitosamente', 'success')
                return redirect(url_for('intervenciones.intervenciones_get_all'))
            else:
                error_message = response.get('message', 'Error desconocido al crear la intervención.')
                flash(error_message, 'warning')
                return render_template('intervenciones_form.html', headers=headers, form_action=url_for('intervenciones.intervenciones_post'), form_method='POST', form_data=form_data, opciones_diagnosticos=opciones_diagnosticos)
        except Exception as e:
            flash('Error inesperado al crear la intervención: ' + str(e), 'warning')

    return render_template('intervenciones_form.html', headers=headers, form_action=url_for('intervenciones.intervenciones_post'), form_method='POST', form_data=form_data, opciones_diagnosticos=opciones_diagnosticos)