# app/controllers/permisos_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
import requests
from app.config import Config

userspermissions_bp = Blueprint('userspermissions', __name__)

# Ruta
ruta_userspermissions_get_all = '/userspermissions/get/all'


@userspermissions_bp.route(ruta_userspermissions_get_all, methods=['GET'])
def userspermissions_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Permisos"
    }
    
    authorized = False
    if ruta_userspermissions_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de usuarios y roles de la API
        response_permissions = api_client.get_data(ruta_userspermissions_get_all)
        

        if response_permissions['status'] == 'success':
            data_permissions = response_permissions['data']  # Extrae la lista de los roles
            message = f"{session['username']}: listado de permisos obtenido!"
        else:
            message = f"Error en la respuesta de la API (permiso): {response_permissions.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_permissions = []  # Asegúrate de pasar una lista vacía en caso de error


        # Crear un diccionario para mapear id_especialidad a especialidad
        permissions_dict = {permission['id_permission']: permission['permission'] for permission in data_permissions}

        # Agregar el nombre de la especialidad a cada diagnóstico y renombrar las claves
        renamed_permissions = []
        for permission in data_permissions:
            permission['permission'] = permissions_dict.get(permission['id_permission'], "Desconocido")  # Si no se encuentra el id_role
            renamed_permission = {
                "ID": permission['id_permission'],
                "Permiso": permission['permission'],
                #"Apellidos": staff['apellidos'],
                # "Documento": user['usernumdoc'],
                #"Staff Tipo": staff['staff_tipo'],
                # "Bloqueado": "Sí" if role['is_blocked'] else "No",
                # "Fecha de Bloqueo": role['blocked_at'] if role['blocked_at'] else "-",
                # "Bloqueado": role['is_blocked'],
                # "Fecha de Bloqueo": role['blocked_at'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_permissions.append(renamed_permission)

        data = renamed_permissions
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de permisos: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('permisos_view.html', data=data, headers=headers)