# app/controllers/roles_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
import requests
from app.config import Config

usersroles_bp = Blueprint('usersroles', __name__)

ruta_usersroles_get_all = '/usersroles/get/all'
@usersroles_bp.route(ruta_usersroles_get_all, methods=['GET'])
def usersroles_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Roles de Usuarios"
    }
    
    authorized = False
    if ruta_usersroles_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de usuarios y roles de la API
        response_usersroles = api_client.get_data(ruta_usersroles_get_all)
        

        if response_usersroles['status'] == 'success':
            data_usersroles = response_usersroles['data']  # Extrae la lista de los roles
            message = f"{session['username']}: listado de roles obtenido!"
        else:
            message = f"Error en la respuesta de la API (role): {response_usersroles.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_usersroles = []  # Asegúrate de pasar una lista vacía en caso de error


        # Crear un diccionario para mapear id_especialidad a especialidad
        usersroles_dict = {userrol['id_role']: userrol['role'] for userrol in data_usersroles}

        # Agregar el nombre de la especialidad a cada diagnóstico y renombrar las claves
        renamed_roles = []
        for role in data_usersroles:
            role['role'] = usersroles_dict.get(role['id_role'], "Desconocido")  # Si no se encuentra el id_role
            renamed_role = {
                "ID": role['id_role'],
                "Role": role['role'],
                #"Apellidos": staff['apellidos'],
                # "Documento": user['usernumdoc'],
                #"Staff Tipo": staff['staff_tipo'],
                "Bloqueado": "Sí" if role['is_blocked'] else "No",
                "Fecha de Bloqueo": role['blocked_at'] if role['blocked_at'] else "-",
                # "Bloqueado": role['is_blocked'],
                # "Fecha de Bloqueo": role['blocked_at'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_roles.append(renamed_role)

        data = renamed_roles
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de roles: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('roles_view.html', data=data, headers=headers)