# app/controllers/users_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

users_bp = Blueprint('users', __name__)

# Rutas
ruta_users_get_all = '/users/get/all'
ruta_users_post = '/users/post'
ruta_users_put = '/users/put'
ruta_users_get_by_id = '/users/get/id'  # Nueva ruta para obtener datos del usuario por ID

# Adicionales
ruta_usersroles_get_all = '/usersroles/get/all'

# Ruta para traer todos los usuarios
@users_bp.route(ruta_users_get_all, methods=['GET'])
def users_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Users"
    }
    
    authorized = False
    if ruta_users_get_all in session.get('permissions', []) and ruta_usersroles_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
    
    api_client = current_app.api_client
    data = []

    try:
        response_users = api_client.get_data(ruta_users_get_all)
        response_roles = api_client.get_data(ruta_usersroles_get_all)

        if response_users['status'] == 'success':
            data_users = response_users['data']
            message = f"Listado de usuarios obtenido!"
        else:
            message = f"Error en la respuesta de la API (usuarios): {response_users.get('message', 'Error desconocido')}"
            flash(message, 'warning')
            data_users = []

        if response_roles['status'] == 'success':
            data_roles = response_roles['data']
            message += f" y roles obtenidos!"
        else:
            message += f" Error en la respuesta de la API (roles): {response_roles.get('message', 'Error desconocido')}"
            flash(message, 'warning')
            data_roles = []

        roles_dict = {role['id_role']: role['role'] for role in data_roles}

        renamed_users = []
        for user in data_users:
            user['role'] = roles_dict.get(user['id_role'], "")
            renamed_user = {
                "ID": user['id_user'],
                "Nombre": user['username'],
                "Correo electrónico": user['email'],
                "Documento": user['usernumdoc'],
                "Rol": user['role'],
                "Bloqueado": "Sí" if user['is_blocked'] else "No",
                "Fecha de Bloqueo": user['blocked_at'] if user['blocked_at'] else "-",
                #"Acciones": f'<a href="/users/put?id_user={user["id_user"]}" class="btn btn-primary" data-id="{user["id_user"]}" data-action="edit">Editar</a>'
                "Acciones": f'''
                    <form action="{url_for('users.users_put')}" method="POST" style="display:inline;">
                        <input type="hidden" name="id_user" value="{user['id_user']}">
                        <button type="submit" class="btn btn-primary">Editar</button>
                    </form>
                    '''
            }
            renamed_users.append(renamed_user)

        data = renamed_users
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de usuarios: {str(e)}"
        flash(message, 'warning')
        data = []

    return render_template('users_view.html', data=data, headers=headers)

@users_bp.route(ruta_users_post, methods=['POST', 'GET'])
def users_post():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Crear Usuario"
    }

    authorized = ruta_users_post in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para crear usuarios (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))

    data = {
            'username': '',
            'usernumdoc': '',
            'email': '',
            'password': ''
        }
    
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'usernumdoc': request.form.get('usernumdoc'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        
        api_client = current_app.api_client
        response = api_client.post_data(ruta_users_post, data)
        
        if response.get('status') == 'success':
            flash('Usuario creado exitosamente!', 'success')
            return redirect(url_for('users.users_get_all'))
        else:
            error_message = response.get('message', 'Error desconocido al crear el usuario.')
            flash(error_message, 'warning')
            return render_template('users_form.html', headers=headers, form_action=url_for('users.users_post'), form_method='POST', form_data=data)
        
    return render_template('users_form.html', headers=headers, form_action=url_for('users.users_post'), form_method='POST', form_data=data)

# Ruta para editar un usuario existente
@users_bp.route(ruta_users_put, methods=['POST', 'GET'])
def users_put():
    headers = {
        "app": Config.APP_TITLE,
        "section": "Editar Usuario"
    }

    authorized = ruta_users_put in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para editar usuarios (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('users.users_get_all'))

    api_client = current_app.api_client

    if request.method == 'POST':
        id_user = request.form.get('id_user')
        if not id_user:
            flash("ID de usuario no proporcionado.", 'warning')
            return redirect(url_for('users.users_get_all'))

        try:
            response = api_client.post_data(ruta_users_get_by_id, {'id_user': id_user})
            if response['status'] == 'success':
                user_data = response['data']
                return render_template('users_form.html', headers=headers, form_action=url_for('users.users_put'), form_method='POST', form_data=user_data)
            else:
                flash(f"Error al obtener datos del usuario: {response.get('message', 'Error desconocido')}", 'warning')
                return redirect(url_for('users.users_get_all'))
        except requests.RequestException as e:
            flash(f"Error al comunicarse con la API: {str(e)}", 'warning')
            return redirect(url_for('users.users_get_all'))

    data = request.get_json()  # Obtener datos en formato JSON
    id_user = data.get('id_user')  # Obtener el ID del usuario

    if not id_user:
        flash("ID de usuario no proporcionado.", 'warning')
        return redirect(url_for('users.users_get_all'))

    # Validar si el usuario está bloqueado antes de permitir la actualización
    try:
        user_response = api_client.post_data(ruta_users_get_by_id, {'id_user': id_user})
        if user_response['status'] == 'success' and user_response['data']['is_blocked']:
            flash("No se puede actualizar el usuario porque está bloqueado.", 'warning')
            return redirect(url_for('users.users_get_all'))
    except requests.RequestException as e:
        flash(f"Error al comunicarse con la API: {str(e)}", 'warning')
        return redirect(url_for('users.users_get_all'))

    update_data = {
        'username': data.get('username'),
        'usernumdoc': data.get('usernumdoc'),
        'email': data.get('email'),
        'password': data.get('password')
    }

    try:
        response = api_client.post_data(f'{ruta_users_put}/{id_user}', update_data)
        if response['status'] == 'success':
            flash('Usuario actualizado exitosamente!', 'success')
            return redirect(url_for('users.users_get_all'))
        else:
            flash(f"Error al actualizar usuario: {response.get('message', 'Error desconocido')}", 'warning')
    except requests.RequestException as e:
        flash(f"Error al comunicarse con la API: {str(e)}", 'warning')

    return redirect(url_for('users.users_get_all'))
