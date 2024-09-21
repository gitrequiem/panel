# app/controllers/pacientes_controller.py

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
import requests
from app.config import Config

pacientes_bp = Blueprint('pacientes', __name__)

# Ruta
ruta_pacientes_get_all = '/pacientes/get/all'
ruta_pacientes_post = '/pacientes/post'
ruta_pacientes_put_id = '/pacientes/put/id'

# Rutas adicionales
ruta_doctipos_get_all = '/doctipos/get/all'
ruta_localidades_get_all = '/localidades/get/all'
ruta_provincias_get_all = '/provincias/get/all'
ruta_nacionalidades_get_all = '/nacionalidades/get/all'
ruta_localidades_get_provincia_id = '/localidades/get/provincias/id'
ruta_pacientes_get_id = '/pacientes/get/id'

@pacientes_bp.route(ruta_pacientes_get_all, methods=['GET'])
def pacientes_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Pacientes"
    }
  
    authorized = False
    if ruta_pacientes_get_all and ruta_doctipos_get_all and ruta_localidades_get_all and ruta_provincias_get_all and ruta_nacionalidades_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    data = []

    try:
        # Obtener datos de la API
        response_pacientes = api_client.get_data(ruta_pacientes_get_all)
        response_doctipos = api_client.get_data(ruta_doctipos_get_all)
        response_provincias = api_client.get_data(ruta_provincias_get_all)
        response_localidades = api_client.get_data(ruta_localidades_get_all)

        response_nacionalidades = api_client.get_data(ruta_nacionalidades_get_all)

        if response_pacientes['status'] == 'success':
            data_pacientes = response_pacientes['data']  # Extrae la lista 
            message = f"{session['username']}: listado de pacientes obtenido!"
        else:
            message = f"Error en la respuesta de la API (pacientes): {response_pacientes.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_pacientes = []  # Asegúrate de pasar una lista vacía en caso de error

        if response_doctipos['status'] == 'success':
            data_doctipos = response_doctipos['data']  # Extrae la lista 
            message += f" y tipos de documento obtenidos!"
        else:
            message += f"Error en la respuesta de la API (doctipos): {response_doctipos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_doctipos = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_localidades['status'] == 'success':
            data_localidades = response_localidades['data']  # Extrae la lista 
            message += f" y localidades obtenidos!"
        else:
            message += f"Error en la respuesta de la API (localidades): {response_localidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_localidades = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_nacionalidades['status'] == 'success':
            data_nacionalidades = response_nacionalidades['data']  # Extrae la lista 
            message += f" y nacionalidades obtenidos!"
        else:
            message += f"Error en la respuesta de la API (nacionalidades): {response_nacionalidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_nacionalidades = []  # Asegúrate de pasar una lista vacía en caso de error
        
        if response_provincias['status'] == 'success':
            data_provincias = response_provincias['data']  # Extrae la lista 
            message += f" y provincias obtenidos!"
        else:
            message += f"Error en la respuesta de la API (provincias): {response_provincias.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_provincias = []  # Asegúrate de pasar una lista vacía en caso de error

        # Crear un diccionario para mapear las entidades dependientes
        doctipos_dict = {doctipo['id_doc_tipo']: doctipo['doc_tipo'] for doctipo in data_doctipos}
        localidades_dict = {}
        for localidad in data_localidades:
            id_provincia = localidad.get('id_provincia')
        if id_provincia:
            localidades_dict.setdefault(id_provincia, {})[localidad['id_localidad']] = localidad['localidad']
       
        provincias_dict = {provincia['id_provincia']: provincia['provincia'] for provincia in data_provincias}
        nacionalidades_dict = {nacionalidad['id_nacionalidad']: nacionalidad['nacionalidad'] for nacionalidad in data_nacionalidades}

        # Agregar el nombre y renombrar las claves
        renamed_pacientes = []
        for paciente in data_pacientes:
            
            paciente['doctipos'] = doctipos_dict.get(paciente['id_doc_tipo'], "Desconocido")  # Si no se encuentra el id
            provincia_id = paciente.get('id_provincia')
            localidad_id = paciente.get('id_localidad')
            if provincia_id:
                paciente['localidades'] = localidades_dict.get(provincia_id, {}).get(localidad_id, "Desconocido")
                paciente['provincias'] = provincias_dict.get(provincia_id, "Provincia desconocida")
            else:
                paciente['localidades'] = "Provincia desconocida"
                paciente['provincias'] = "Provincia desconocida"
         
            paciente['nacionalidades'] = nacionalidades_dict.get(paciente['id_nacionalidad'], "Desconocido")  # Si no se encuentra el id
            renamed_paciente = {
                "ID": paciente['id_paciente'],
                "Nombre": paciente['nombre'],
                "Apellidos": paciente['apellidos'],
                "Tipo de Doc.": paciente['doc_tipo'],
                "Número de Doc.": paciente['doc_numero'],
                "Localidad": paciente['localidad'],
                "Nacionalidad": paciente['nacionalidad'],
                "Acciones": f'''
                    <form action="{url_for('pacientes.pacientes_put')}" method="POST" style="display:inline;">
                        <input type="hidden" name="id_paciente" value="{paciente['id_paciente']}">
                        <button type="submit" class="btn btn-primary">Editar</button>
                    </form>
      
                    <form action="{url_for('cirugias.cirugias_post')}" method="POST" style="display:inline;">
                        <input type="hidden" name="id_paciente" value="{paciente['id_paciente']}">
                        <button type="submit" class="btn btn-primary">Cirugía</button>
                    </form>'''
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                #"Acciones": f'<a href="#" class="btn btn-primary">Ver</a>'
            }
            renamed_pacientes.append(renamed_paciente)

        data = renamed_pacientes
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de pacientes: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('pacientes_view.html', data=data, headers=headers)

# Ruta para crear un paciente
@pacientes_bp.route(ruta_pacientes_post, methods=['GET','POST'])
def pacientes_post():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Pacientes"
    }
  
    authorized = False
    if ruta_pacientes_get_all and ruta_pacientes_post and ruta_doctipos_get_all and ruta_localidades_get_all \
            and ruta_provincias_get_all and ruta_nacionalidades_get_all in session.get('permissions', []):
        authorized = True
        
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))
        
    api_client = current_app.api_client
    
    try:
        response_doctipos = api_client.get_data(ruta_doctipos_get_all) # accede a la ruta del get all de tipos de documentos de la api
        response_localidades = api_client.get_data(ruta_localidades_get_all)
        response_provincias = api_client.get_data(ruta_provincias_get_all)
        response_nacionalidades = api_client.get_data(ruta_nacionalidades_get_all)
         
        if response_doctipos.get('status') == 'success':
            doc_tipos = response_doctipos.get('data', [])
        else:
            flash('Error al obtener los tipos de documentos', 'error')
            doc_tipos = {}
            
        if response_nacionalidades.get('status') == 'success':
            nacionalidades = response_nacionalidades.get('data', [])
        else:
            flash('Error al obtener las nacionalidades', 'error')
            nacionalidades = {}
        
        if response_localidades['status'] == 'success':
            localidades = response_localidades['data']
        else:
            # Manejar el error si no se obtuvieron las localidades
            flash('Error al obtener las localidades', 'error')
            opciones_localidades = {}
            
        if response_provincias['status'] == 'success':
            provincias = response_provincias['data']
        else:
            # Manejar el error si no se obtuvieron las provincias
            flash('Error al obtener las provincias', 'error')
            opciones_provincias = {}
        
    except requests.RequestException as e:
        message = f"Error inesperado al obtener los datos necesarios para crear un paciente nuevo {str(e)}"
        flash(message, 'warning')        

    # Listas para desplegables como diccionarios
    # Crear opciones para el desplegable de tipos de documentos y un diccionario para búsqueda rápida
    opciones_doc_tipos = [
        {
            'doc_tipo': doc_tipo['doc_tipo'], 
            'id_doc_tipo':doc_tipo['id_doc_tipo']
        } 
        for doc_tipo in doc_tipos
    ]
        
    # Crear opciones para el desplegable de nacionalidades y un diccionario para búsqueda rápida
    opciones_nacionalidades = [
        {
            'nacionalidad':nacionalidad['nacionalidad'], 
            'id_nacionalidad':nacionalidad['id_nacionalidad']
        }
        for nacionalidad in nacionalidades
    ]
    
    # Crear opciones para el desplegable de provincias
    opciones_provincias = [
        {
            'provincia': provincia['provincia'], 
            'id_provincia':provincia['id_provincia']
        }
        for provincia in provincias
    ]
      
    # Crear opciones para el desplegable de localidades como una lista de diccionarios
    opciones_localidades = [
        {
            'localidad': localidad['localidad'],
            'id_localidad': localidad['id_localidad'],
            'id_provincia': localidad['id_provincia']
        } 
        for localidad in localidades
    ]
    
    form_data = {
        'nombre':'',
        'apellidos':''  
    }
    
    if request.method == 'POST':
        # Obtener datos del formulario
        form_data['nombre'] = request.form['nombre']
        form_data['apellidos'] = request.form['apellidos']
        nacionalidad_seleccionada = request.form['id_nacionalidad']  # Nombre o ID de la nacionalidad seleccionada
        doc_tipo_seleccionado = request.form['id_doc_tipo'] # Nombre o ID del tipo de documento seleccionado
        doc_numero = request.form['doc_numero']
        localidad_seleccionada = request.form['id_localidad'] # Nombre o ID de la localidad seleccionada
        
        try:
            nacionalidad_seleccionada = int(nacionalidad_seleccionada) # para que tome el id en vez del string
        except ValueError:
            flash("La nacionalidad seleccionada no es válida.", "error")
            return render_template('pacientes_form.html', headers=headers, form_action=url_for('pacientes.pacientes_post'), form_method='POST', form_data=form_data, \
                opciones_doc_tipos=opciones_doc_tipos, opciones_nacionalidades=opciones_nacionalidades, \
                opciones_provincias=opciones_provincias, opciones_localidades=opciones_localidades)
        try:
            doc_tipo_seleccionado = int(doc_tipo_seleccionado) # para que tome el id en vez del string
        except ValueError:
            flash("El tipo de documento seleccionado no es válido.", "error")
            return render_template('pacientes_form.html', headers=headers, form_action=url_for('pacientes.pacientes_post'), form_method='POST', form_data=form_data, \
                opciones_doc_tipos=opciones_doc_tipos, opciones_nacionalidades=opciones_nacionalidades, \
                opciones_provincias=opciones_provincias, opciones_localidades=opciones_localidades)
         
        try:
            localidad_seleccionada = int(localidad_seleccionada) # para que tome el id en vez del string
        except ValueError:
            flash("La localidad seleccionada no es válida.", "error")
            return render_template('pacientes_form.html', headers=headers, form_action=url_for('pacientes.pacientes_post'), form_method='POST', form_data=form_data, \
                opciones_doc_tipos=opciones_doc_tipos, opciones_nacionalidades=opciones_nacionalidades, \
                opciones_provincias=opciones_provincias, opciones_localidades=opciones_localidades)
            
        # Crear el JSON para enviar a la API
        data = {
            'nombre': form_data['nombre'],
            'apellidos' : form_data['apellidos'],
            'id_doc_tipo': doc_tipo_seleccionado,
            'doc_numero' : doc_numero,
            'id_nacionalidad' : nacionalidad_seleccionada,
            'id_localidad' : localidad_seleccionada
        }
        
        # Enviar datos a la API para crear el nuevo paciente
        try:
            response = api_client.post_data(ruta_pacientes_post, data)
            if response.get('status') == 'success':
                flash('Paciente creado exitosamente', 'success')
                return redirect(url_for('pacientes.pacientes_get_all'))
            else:
                error_message = response.get('message', 'Error desconocido al crear el paciente.')
                flash(error_message, 'warning')
                return render_template('pacientes_form.html', headers=headers, form_action=url_for('pacientes.pacientes_post'),  form_method='POST', form_data=form_data, \
                    opciones_doc_tipos=opciones_doc_tipos, opciones_nacionalidades=opciones_nacionalidades, \
                    opciones_provincias=opciones_provincias, opciones_localidades=opciones_localidades)
        except Exception as e:
            flash('Error inesperado al crear el paciente: ' + str(e), 'warning')

    return render_template('pacientes_form.html', headers=headers, form_action=url_for('pacientes.pacientes_post'),  form_method='POST', form_data=form_data, \
                    opciones_doc_tipos=opciones_doc_tipos, opciones_nacionalidades=opciones_nacionalidades, \
                    opciones_provincias=opciones_provincias, opciones_localidades=opciones_localidades)


# ruta para editar un paciente
@pacientes_bp.route(ruta_pacientes_put_id, methods=['PUT','POST'])
def pacientes_put():
    
    message = ''
    headers = {
        "app":Config.APP_TITLE,
        "section": "Editar Paciente"
    }
    
    authorized = ruta_pacientes_put_id and ruta_doctipos_get_all and ruta_pacientes_get_id and ruta_localidades_get_all and ruta_nacionalidades_get_all in session.get('permissions', [])
    if not authorized:
        message = "Usuario no autorizado para editar un paciente (permissions err)"
        flash(message, 'error')
        return redirect(url_for('index.index'))

    api_client = current_app.api_client
    
    if request.method == 'POST':
        id_paciente = request.form.get('id_paciente')
        paciente_data = {}
        
        try:
            response_paciente = api_client.post_data(ruta_pacientes_get_id, {'id_paciente':id_paciente})
            if response_paciente['status'] == 'success':
                paciente_data = response_paciente['data']
                print(paciente_data)
            else:
                message = f"Error al obtener los datos del paciente: {response_paciente.get('message', 'Error desconocido')}"
                flash(message, 'warning')
                return redirect(url_for('pacientes.pacientes_get_all'))

            response_doctipos = api_client.get_data(ruta_doctipos_get_all) # accede a la ruta del get all de tipos de documentos de la api
            response_localidades = api_client.get_data(ruta_localidades_get_all)
            response_nacionalidades = api_client.get_data(ruta_nacionalidades_get_all)
         
            if response_doctipos.get('status') == 'success':
                doc_tipos = response_doctipos.get('data', [])
            else:
                flash('Error al obtener los tipos de documentos', 'error')
                doc_tipos = []
            
            if response_nacionalidades.get('status') == 'success':
                nacionalidades = response_nacionalidades.get('data', [])
            else:
                flash('Error al obtener las nacionalidades', 'error')
                nacionalidades = []
            
            if response_localidades['status'] == 'success':
                localidades = response_localidades['data']
                # Crear opciones para el desplegable de localidades
                opciones_localidades = [(localidad['id_localidad'], localidad['localidad']) for localidad in localidades]
            else:
                # Manejar el error si no se obtuvieron las localidades
                flash('Error al obtener las localidades', 'error')
                opciones_localidades = []
            # Crear opciones para el desplegable de tipos de documentos y un diccionario para búsqueda rápida
            opciones_doc_tipos = [(doc_tipo['doc_tipo'], doc_tipo['id_doc_tipo']) for doc_tipo in doc_tipos]
                
            # Crear opciones para el desplegable de nacionalidades y un diccionario para búsqueda rápida
            opciones_nacionalidades = [(nacionalidad['nacionalidad'], nacionalidad['id_nacionalidad']) for nacionalidad in nacionalidades]
            
            # Crear opciones para el desplegable de localidades y un diccionario para búsqueda rápida
            opciones_localidades = [(localidad['localidad'], localidad['id_localidad'])for localidad in localidades]

            return render_template('pacientes_form_edit.html',
                               headers=headers,
                               form_data=paciente_data,
                               opciones_doc_tipos=opciones_doc_tipos,
                               opciones_localidades=opciones_localidades,opciones_nacionalidades=opciones_nacionalidades)
       
        except requests.exceptions.HTTPError as e:
            # Manejo de errores
            if e.response.status_code == 403:
                message = "Acceso denegado para obtener los datos del paciente"
            else:
                message = f"Error al obtener los datos del paciente: {str(e)}"
                flash(message, 'error')
                return redirect(url_for('pacientes.pacientes_get_all'))
    
    elif request.method == 'PUT':
        data = request.get_json()  # Obtener datos en formato JSON
        id_paciente = data.get('id_paciente')  # Obtener el ID del paciente

        # Valida data 
        if not data:
            message = "No se recibieron datos en la solicitud"
            flash(message, 'error')
            return jsonify({'message': message}), 400
        
        id_nacionalidad = data.get('nacionalidad')  # Obtener el valor de nacionalidad y asignarlo a id_nacionalidad   
        
        # Crea el update_paciente_data 
        update_paciente_data = {
            'id_paciente': data.get('id_paciente'),
            'nombre': data.get('nombre'),
            'apellidos': data.get('apellidos'),
            'id_doc_tipo': data.get('doc_tipo'),
            'doc_numero' : data.get('doc_numero'),
            'id_nacionalidad': id_nacionalidad,
            'id_localidad': data.get('id_localidad')
            }

        # Actualiza la data del paciente en la API
        try:
            response = api_client.put_data(ruta_pacientes_put_id, update_paciente_data)
            if response['status'] == 'success':
                flash('Paciente actualizado exitosamente', 'success')
                return jsonify({'message': 'Paciente actualizado exitosamente'}), 200
            else:
                message = f"Error al actualizar el paciente: {response.get('message', 'Error desconocido')}"
                flash(message, 'error')
                return jsonify({'message': message}), 400
        except requests.RequestException as e:
            message = f"Error inesperado al actualizar el paciente: {str(e)}"
            flash(message, 'error')
            return redirect(url_for('pacientes.pacientes_get_all'))
    return render_template('pacientes_form_edit.html', headers=headers, form_action=url_for('pacientes.pacientes_put', id_paciente=id_paciente), form_method='PUT', form_data=paciente_data, opciones_doc_tipos=opciones_doc_tipos, opciones_localidades=opciones_localidades, opciones_nacionalidades=opciones_nacionalidades)    
