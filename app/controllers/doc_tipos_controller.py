# app/controllers/doc_tipos_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

# Create a new Blueprint for document types
doctipos_bp = Blueprint('doctipos', __name__)

# rutas
ruta_doctipos_get_all = '/doctipos/get/all'

# ruta para traer todos los users
@doctipos_bp.route(ruta_doctipos_get_all, methods=['GET'])
def doctipos_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Tipos de Documentos"
    }
    
    # permisos
    authorized = False
    if ruta_doctipos_get_all in session.get('permissions', []):
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
        response_doctipos = api_client.get_data(ruta_doctipos_get_all)        # principal
        

        # obtener rta de la api para la consulta principal
        if response_doctipos['status'] == 'success':
            data_doctipos = response_doctipos['data']  # Extrae la lista 
            message = f"{session['username']}: listado de tipos de documento obtenido!"
        else:
            message = f"Error en la respuesta de la API (doctipos): {response_doctipos.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_doctipos = []  # Asegúrate de pasar una lista vacía en caso de error


        # Crear un diccionario para mapear id_role a role name
        doctipos_dict = {doctipo['id_doc_tipo']: doctipo['doc_tipo'] for doctipo in data_doctipos}

        # Agregar el nombre del rol a cada usuario y renombrar las claves
        renamed_doctipos = []
        for doctipo in data_doctipos:
            doctipo['doc_tipo'] = doctipos_dict.get(doctipo['id_doc_tipo'], "")  # Si no se encuentra el id
            renamed_doctipo = {
                "ID": doctipo['id_doc_tipo'],
                "Tipo de Documento": doctipo['doc_tipo'],
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones":f'<a href="#" class="btn btn-primary">Editar</a>'
            }
            renamed_doctipos.append(renamed_doctipo)

        data = renamed_doctipos
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de tipos de documento: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('nuevos_pacientes_view.html', data=data, headers=headers)