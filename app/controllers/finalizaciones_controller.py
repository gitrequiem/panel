# app/controllers/finalizaciones_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

finalizaciones_bp = Blueprint('finalizaciones', __name__)

# rutas
ruta_finalizaciones_get_all = '/finalizaciones/get/all'
ruta_finalizaciones_post = '/finalizaciones/post'

# ruta para traer todas las finalizaciones
@finalizaciones_bp.route(ruta_finalizaciones_get_all, methods=['GET'])
def finalizaciones_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Finalizaciones"
    }
    
    # permisos
    authorized = False
    if ruta_finalizaciones_get_all in session.get('permissions', []):
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
        response_finalizaciones = api_client.get_data(ruta_finalizaciones_get_all)   # principal
        

        # obtener rta de la api para la consulta principal
        if response_finalizaciones['status'] == 'success':
            data_finalizaciones = response_finalizaciones['data']  # Extrae la lista de finalizaciones
            message = f"{session['username']}: listado de finalizaciones obtenido!"
        else:
            message = f"Error en la respuesta de la API (finalizaciones): {response_finalizaciones.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_finalizaciones = []  # Asegúrate de pasar una lista vacía en caso de error

        # Agregar el nombre del rol a cada usuario y renombrar las claves
        renamed_finalizaciones = []
        for finalizacion in data_finalizaciones:
            #user['role'] = roles_dict.get(user['id_role'], "")  # Si no se encuentra el id_role
            renamed_finalizacion = {
                "ID": finalizacion['id_finalizacion'],
                "Tipo de Finalización": finalizacion['finalizacion'],
                "Realizada": "Sí" if finalizacion['realizada'] else "No",
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'''
                    <form action="#" method="POST" style="display:inline;">
                        <input type="hidden" name="id_finalizacion" value="{finalizacion['id_finalizacion']}">
                        <button type="submit" class="btn btn-primary">Editar</button>
                    </form>
                    '''
                # "Acciones": f'<a href="#" class="btn btn-primary">Rol</a>' '&nbsp;' 
                #             f'<a href="#" class="btn btn-primary">Block</a>' '&nbsp;' 
                #             f'<a href="#" class="btn btn-primary">Editar</a>'
            }
            renamed_finalizaciones.append(renamed_finalizacion)

        data = renamed_finalizaciones
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de finalizaciones: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('finalizaciones_view.html', data=data, headers=headers)

# ruta para crear un tipo de finalización
@finalizaciones_bp.route(ruta_finalizaciones_post, methods=['POST', 'GET'])
def finalizaciones_post():
    
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Crear Finalización"
    }

    authorized = ruta_finalizaciones_post in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para crear finalizaciones (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))
    
    data = {
        
        'finalizacion': '',
        'realizada': None
        }
    
    if request.method == 'POST':
               
        data = {
            'finalizacion':request.form.get('finalizacion'),
            'realizada': True if request.form.get('realizada') == 'on' else False
            }
        
        api_client = current_app.api_client
        response = api_client.post_data(ruta_finalizaciones_post, data)
        
        if response.get('status') == 'success':
            flash('Finalización creada exitosamente!', 'success')
            return redirect(url_for('finalizaciones.finalizaciones_get_all'))
        else:
            error_message = response.get('message', 'Error desconocido al crear la finalización.')
            flash(error_message, 'warning')
            return render_template('finalizaciones_form.html', headers=headers, form_action=url_for('finalizaciones.finalizaciones_post'), form_method='POST', form_data=data)
        
    return render_template('finalizaciones_form.html', headers=headers, form_action=url_for('finalizaciones.finalizaciones_post'), form_method='POST', form_data=data)