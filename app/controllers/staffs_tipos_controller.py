# app/controllers/staffs_roles_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

stafftipos_bp = Blueprint('stafftipos', __name__)

# Ruta
ruta_staff_tipos_get_all = '/stafftipos/get/all'
ruta_staff_tipos_post = '/stafftipos/post'

@stafftipos_bp.route(ruta_staff_tipos_get_all, methods=['GET'])
def staff_tipos_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Tipos de Staff"
    }
    
    authorized = False
    if ruta_staff_tipos_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de la API
        response_staff_tipos = api_client.get_data(ruta_staff_tipos_get_all)

        if response_staff_tipos['status'] == 'success':
            data_staff_tipos = response_staff_tipos['data']  # Extrae la lista 
            message = f"{session['username']}: listado de tipos de staff obtenido!"
        else:
            message = f"Error en la respuesta de la API (tipos de staff): {response_staff_tipos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_staff_tipos = []  # Asegúrate de pasar una lista vacía en caso de error

        # Agregar el nombre  
        renamed_staff_tipos = []
        for staff_tipo in data_staff_tipos:
            renamed_staff_tipo = {
                "ID": staff_tipo['id_staff_tipo'],
                "Tipo de Staff": staff_tipo['staff_tipo'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_staff_tipos.append(renamed_staff_tipo)

        data = renamed_staff_tipos
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de los tipos de staff: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('staffs_tipos_view.html', data=data, headers=headers)

# ruta para crear un tipo de satff
@stafftipos_bp.route(ruta_staff_tipos_post, methods=['POST', 'GET'])
def stafftipos_post():
    
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Crear Tipo de Staff"
    }

    authorized = ruta_staff_tipos_post in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para crear tipos de staff (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))
    
    data = {
        
        'staff_tipo': ''
        
        }
    
    if request.method == 'POST':
               
        data = {
            'staff_tipo':request.form.get('staff_tipo'),
            
            }
        
        api_client = current_app.api_client
        response = api_client.post_data(ruta_staff_tipos_post, data)
        
        if response.get('status') == 'success':
            flash('Tipo de Staff creado exitosamente!', 'success')
            return redirect(url_for('stafftipos.staff_tipos_get_all'))
        else:
            error_message = response.get('message', 'Error desconocido al crear el tipo de staff.')
            flash(error_message, 'warning')
            return render_template('staff_tipos_form.html', headers=headers, form_action=url_for('stafftipos.stafftipos_post'), form_method='POST', form_data=data)
        
    return render_template('staff_tipos_form.html', headers=headers, form_action=url_for('stafftipos.stafftipos_post'), form_method='POST', form_data=data)
