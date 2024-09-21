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
    data = {}

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
            data_staffs = {}  # Asegúrate de pasar una lista vacía en caso de error

        if response_staff_tipos['status'] == 'success':
            data_staff_tipos = response_staff_tipos['data']  # Extrae la lista 
            message += f" y tipos de staff obtenidos!"
        else:
            message += f"Error en la respuesta de la API (staff tipos): {response_staff_tipos.get('message', 'Error desconocido')}"
            flash(message, 'warning')
            data_staff_tipos = {}  # Asegúrate de pasar una lista vacía en caso de error

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
                "Acciones": f'''
                    <form action="  {url_for('staffs.staffs_put')}  " method="POST" style="display:inline;">
                        <input type="hidden" name="origin" id="origin" value="controller">
                        <input type="hidden" name="id_staff" value="{staff['id_staff']}">
                        <button type="submit" class="btn btn-primary">Edit</button>
                    </form>'''
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


# ruta para editar un staff
@staffs_bp.route(ruta_staffs_put_id, methods=['POST'])
def staffs_put():
    
    message = ''
    headers = {
        "app":Config.APP_TITLE,
        "section": "Editar Staff"
    }
    
    # Permisos
    authorized = ruta_staffs_put_id and ruta_staff_tipos_get_all and ruta_staffs_get_id in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para editar staff (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))

    # Instancio api_client y defino el dict para opciones_staff_tipos
    api_client = current_app.api_client
    opciones_staff_tipos = []
    
    # Levanto el origen del post (form o controller)
    origin = request.form.get('origin')

    print("antes del IF")
    # Para cuando vuelve del formulario
    if origin == 'controller':
        print("venimos de controller")
        id_staff = request.form.get('id_staff')
        staff_data = []
        
        try:
            response_staff = api_client.post_data(ruta_staffs_get_id, {'id_staff':id_staff})
            if response_staff['status'] == 'success':
                staff_data = response_staff['data']
                #print(staff_data)
            else:
                message = f"Error al obtener los datos del staff: {response_staff.get('message', 'Error desconocido')}"
                flash(message, 'warning')
                return redirect(url_for('staffs.staffs_get_all'))

            # Obtiene los tipos de staff
            response_staff_tipos = api_client.get_data(ruta_staff_tipos_get_all)
            if response_staff_tipos['status'] == 'success':
                staff_tipos = response_staff_tipos['data']
            else:
                message = f"Error al obtener los tipos de staff: {response_staff_tipos.get('message', 'Error desconocido')}"
                flash(message, 'warning')
                staff_tipos = []

            # Crea las opciones para el desplegable de tipos de staff
            opciones_staff_tipos = [
                {
                    'staff_tipo':staff_tipo['staff_tipo'], 
                    'id_staff_tipo':staff_tipo['id_staff_tipo']
                }
                for staff_tipo in staff_tipos
            ]
                        
            return render_template('staffs_form_edit.html',
                               headers=headers,
                               form_action=url_for('staffs.staffs_put'),  
                               form_method='POST',
                               form_data=staff_data,
                               opciones_staff_tipos=opciones_staff_tipos)
       
        except requests.exceptions.HTTPError as e:
            # Manejo de errores
            if e.response.status_code == 403:
                message = "Acceso denegado para obtener los datos del staff"
            else:
                message = f"Error al obtener los datos del staff: {str(e)}"
                flash(message, 'error')
                return redirect(url_for('staffs.staffs_get_all'))
    
    # Para que vaya al formulario
    elif origin == 'form':

        print("venimos del form")
        # obtiene la data del formulario        
        data = request.form  # Obtener datos (NO ES JSON)        
        
        id_staff = data.get('id_staff')  # Obtener el ID del staff
        # Valida data 
        if not data:
            message = "No se recibieron datos en la solicitud"
            flash(message, 'error')
            return jsonify({'message': message}), 400
            
        # Crea el update_staff_data 
        update_staff_data = {
            'id_staff': data.get('id_staff'),
            'nombres': data.get('nombres'),
            'apellidos': data.get('apellidos'),
            'id_staff_tipo': data.get('id_staff_tipo')
            }
        print("2 ya esta la data para el update")
        print(update_staff_data)
        
        # Actualiza la data de staff en la API
        try:
            print("estamos en el try")
            response = api_client.put_data(ruta_staffs_put_id, update_staff_data)
            print(response)
            if response.get('status') == 'success':
                flash('Staff actualizado exitosamente', 'success')
                # return jsonify({'message': 'Staff actualizado exitosamente'}), 200
                return redirect(url_for('staffs.staffs_get_all')), print("estamos en el return")
            else:
                print("estamos en else")
                message = f"Error al actualizar el staff: {response.get('message', 'Error desconocido')}"
                flash(message, 'error')
                return jsonify({'message': message}), 400
            
        except requests.RequestException as e:
            message = f"Error inesperado al actualizar el staff: {str(e)}"
            flash(message, 'error')
            return redirect(url_for('staffs.staffs_get_all'))
        
    return render_template('staffs_form_edit.html', headers=headers, form_action=url_for('staffs.staffs_put'), form_method='POST', form_data=staff_data, opciones_staff_tipos=opciones_staff_tipos)    
