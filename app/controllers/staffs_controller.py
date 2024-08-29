# app/controllers/staffs_controller.py

from flask import Blueprint, current_app, flash, json, jsonify, redirect, render_template, request, session, url_for
import requests
from app.config import Config

staffs_bp = Blueprint('staffs', __name__)

# Bp adicional
stafftipos_bp = Blueprint('stafftipos', __name__)

# Ruta
ruta_staffs_get_all = '/staffs/get/all'
ruta_staffs_post = '/staffs/post'
ruta_staffs_get_id = '/staffs/get/id'
ruta_staffs_put_id = '/staffs/put/id'

# Rutas adicionales
ruta_staff_tipos_get_all = '/stafftipos/get/all'

# Ruta para traer todo el staff
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
            flash(message, 'warning')
            data_staffs = []  # Asegúrate de pasar una lista vacía en caso de error

        if response_staff_tipos['status'] == 'success':
            data_staff_tipos = response_staff_tipos['data']  # Extrae la lista 
            message += f" y tipos de staff obtenidos!"
        else:
            message += f"Error en la respuesta de la API (staff tipos): {response_staff_tipos.get('message', 'Error desconocido')}"
            flash(message, 'warning')
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
                #"Acciones": f'<button class="btn btn-primary edit-button" data-staff-id="{{ staff.id_staff }}">Editar</button>'
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                #"Acciones": f'<a href="#" class="btn btn-primary">Ver</a>',
                #"Acciones": f'<a href="{url_for('staffs.staffs_put', id_staff=staff["id_staff"])}" class="btn btn-primary">Editar</a>'
                "Acciones": f'''
                    <form action="{url_for('staffs.staffs_put')}" method="POST" style="display:inline;">
                        <input type="hidden" name="id_staff" value="{staff['id_staff']}">
                        <button type="submit" class="btn btn-primary">Editar</button>
                    </form>
                    '''
                
            }
            renamed_staffs.append(renamed_staff)

        data = renamed_staffs
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado del staff: {str(e)}"
        flash(message, 'warning')
        data = []

    return render_template('staffs_view.html', data=data, headers=headers)

# ruta para crear un staff
@staffs_bp.route(ruta_staffs_post, methods=['POST', 'GET'])
def staffs_post():
    message = ''

    headers = {
        "app": Config.APP_TITLE,
        "section": "Crear Staff"
    }

    authorized = ruta_staffs_post and ruta_staff_tipos_get_all in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para crear staff (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))
    api_client = current_app.api_client

    try:
        response = api_client.get_data(ruta_staff_tipos_get_all) # accede a la ruta del get all de tipos de staff de la api
        if response.get('status') == 'success':
            staff_tipos = response.get('data', [])
        else:
            flash('Error al obtener los tipos de staff', 'error')
            staff_tipos = []
    except Exception as e:
        flash('Error inesperado al obtener los tipos de staff', 'error')
        staff_tipos = []

    # Crear opciones para el desplegable de tipos de staff y un diccionario para búsqueda rápida
    opciones_staff_tipos = [(staff_tipo['staff_tipo'], staff_tipo['id_staff_tipo']) for staff_tipo in staff_tipos]
    
    print(opciones_staff_tipos) # imprime por consola los tipos de staff para asegurarme que funciona.

    form_data = {
        'apellidos': '',
        'nombres': ''
    }

    if request.method == 'POST':
        # Obtener datos del formulario
        form_data['apellidos'] = request.form['apellidos']
        form_data['nombres'] = request.form['nombres']
        staff_tipo_seleccionado = request.form['staff_tipo']  # Nombre o ID del staff_tipo seleccionado
        
        try:
            staff_tipo_seleccionado = int(staff_tipo_seleccionado) # para que tome el id en vez del string
        except ValueError:
            flash("El tipo de staff seleccionado no es válido.", "error")
            return render_template('staffs_form.html', headers=headers, form_action=url_for('staffs.staffs_post'), form_method='POST', form_data=form_data, opciones_staff_tipos=opciones_staff_tipos)

        # Crear el JSON para enviar a la API
        data = {
            'apellidos': form_data['apellidos'],
            'nombres': form_data['nombres'],
            'id_staff_tipo': staff_tipo_seleccionado
        }

        # Enviar datos a la API para crear el nuevo staff
        try:
            response = api_client.post_data(ruta_staffs_post, data)
            if response.get('status') == 'success':
                flash('Staff creado exitosamente', 'success')
                return redirect(url_for('staffs.staffs_get_all'))
            else:
                error_message = response.get('message', 'Error desconocido al crear el staff.')
                flash(error_message, 'warning')
                return render_template('staffs_form.html', headers=headers, form_action=url_for('staffs.staffs_post'), form_method='POST', form_data=form_data, opciones_staff_tipos=opciones_staff_tipos)
        except Exception as e:
            flash('Error inesperado al crear el staff: ' + str(e), 'warning')

    return render_template('staffs_form.html', headers=headers, form_action=url_for('staffs.staffs_post'), form_method='POST', form_data=form_data, opciones_staff_tipos=opciones_staff_tipos)



# ruta para editar un staff ---- NO ANDA TODAVIA        
@staffs_bp.route(ruta_staffs_put_id, methods=['PUT'])
def staffs_put():
   
    message = ''
    headers = {
        "app": Config.APP_TITLE,
        "section": "Editar Staff"
    }

    authorized = ruta_staffs_put_id and ruta_staff_tipos_get_all and ruta_staffs_get_id in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para editar staff (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))
    
    data = request.get_json()
    print("Datos recibidos:", data)
    id_staff = data.get('id_staff')
    
    api_client = current_app.api_client

    try:
        # Get staff data to be edited
        # response_staff = api_client.get_data(f"{ruta_staffs_get_id}/{id_staff}")
        response_staff = api_client.post_data(ruta_staffs_put_id, {'id_staff': id_staff}) #agrego
        
        if response_staff['status'] == 'success':
            staff_data = response_staff['data']
            print(staff_data)
        else:
            message = f"Error al obtener los datos del staff: {response_staff.get('message', 'Error desconocido')}"
            flash(message, 'warning')
            return redirect(url_for('staffs.staffs_get_all'))

        # Get staff types
        response_staff_tipos = api_client.get_data(ruta_staff_tipos_get_all)
        if response_staff_tipos['status'] == 'success':
            staff_tipos = response_staff_tipos['data']
        else:
            message = f"Error al obtener los tipos de staff: {response_staff_tipos.get('message', 'Error desconocido')}"
            flash(message, 'warning')
            staff_tipos = []

        # Create options for the staff types dropdown
        opciones_staff_tipos = [(staff_tipo['staff_tipo'], staff_tipo['id_staff_tipo']) for staff_tipo in staff_tipos]

        if request.method == 'PUT':
            # Get data from the request body
            data = request.get_json()

            # Validate data (add your validations here)
            if not data:
                message = "No se recibieron datos en la solicitud"
                flash(message, 'error')
                return jsonify({'message': message}), 400

            # Update staff data in the API
            try:
                response = api_client.put_data(f"{ruta_staffs_put_id}/{id_staff}", data)
                if response.get('status') == 'success':
                    flash('Staff actualizado exitosamente', 'success')
                    return jsonify({'message': 'Staff actualizado exitosamente'}), 200
                else:
                    message = f"Error al actualizar el staff: {response.get('message', 'Error desconocido')}"
                    flash(message, 'error')
                    return jsonify({'message': message}), 400
            except Exception as e:
                message = f"Error inesperado al actualizar el staff: {str(e)}"
                flash(message, 'error')
                return jsonify({'message': message}), 500

        # If it's a GET request, render the edit form
        return render_template('staffs_form_edit.html', headers=headers, form_action=url_for('staffs.staffs_put', id_staff=id_staff), form_method='PUT', form_data=staff_data, opciones_staff_tipos=opciones_staff_tipos)

    except requests.RequestException as e:
        message = f"Error al obtener los datos del staff: {str(e)}"
        flash(message, 'warning')
        return redirect(url_for('staffs.staffs_get_all'))