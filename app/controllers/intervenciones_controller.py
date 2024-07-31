# app/controllers/intervenciones_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
import requests
from app.config import Config

intervenciones_bp = Blueprint('intervenciones', __name__)

# rutas
ruta_intervenciones_get_all = '/intervenciones/get/all'

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