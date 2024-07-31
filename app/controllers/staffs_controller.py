# app/controllers/staffs_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
import requests
from app.config import Config

staffs_bp = Blueprint('staffs', __name__)

# Ruta
ruta_staffs_get_all = '/staffs/get/all'

# Rutas adicionales
ruta_staff_tipos_get_all = '/stafftipos/get/all'

@staffs_bp.route(ruta_staffs_get_all, methods=['GET'])
def staffs_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Staff"
    }
    
    authorized = False
    if ruta_staffs_get_all and ruta_staff_tipos_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de la API
        response_staffs = api_client.get_data(ruta_staffs_get_all)
        response_staff_tipos = api_client.get_data(ruta_staff_tipos_get_all)

        if response_staffs['status'] == 'success':
            data_staffs = response_staffs['data']  # Extrae la lista 
            message = f"{session['username']}: listado de staff obtenido!"
        else:
            message = f"Error en la respuesta de la API (staff): {response_staffs.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_staffs = []  # Asegúrate de pasar una lista vacía en caso de error

        if response_staff_tipos['status'] == 'success':
            data_staff_tipos = response_staff_tipos['data']  # Extrae la lista 
            message += f" y tipos de staff obtenidos!"
        else:
            message += f"Error en la respuesta de la API (staff tipos): {response_staff_tipos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_staff_tipos = []  # Asegúrate de pasar una lista vacía en caso de error

        # Crear un diccionario para mapear 
        staff_tipos_dict = {staff_tipo['id_staff_tipo']: staff_tipo['staff_tipo'] for staff_tipo in data_staff_tipos}

        # Agregar el nombre y renombrar las claves
        renamed_staffs = []
        for staff in data_staffs:
            staff['staff_tipo'] = staff_tipos_dict.get(staff['id_staff_tipo'], "Desconocido")  # Si no se encuentra el id
            renamed_staff = {
                "ID": staff['id_staff'],
                "Nombres": staff['nombres'],
                "Apellidos": staff['apellidos'],
                "Staff Tipo": staff['staff_tipo'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_staffs.append(renamed_staff)

        data = renamed_staffs
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado del staff: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('staffs_view.html', data=data, headers=headers)