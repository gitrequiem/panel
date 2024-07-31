# app/controllers/tickets_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
import requests
from app.config import Config

tickets_bp = Blueprint('tickets', __name__)

# rutas
ruta_tickets_get_all = '/tickets/get/all'

#adicionales
ruta_ticketsentidades_get_all = '/ticketsentidades/get/all'
ruta_users_get_all = '/users/get/all'

# ruta para traer todos los users
@tickets_bp.route(ruta_tickets_get_all, methods=['GET'])
def tickets_get_all():
    message = ''
    
    headers = {
        "app": Config.APP_TITLE,
        "section": "Tickets"
    }
    
    # permisos
    authorized = False
    if ruta_tickets_get_all and ruta_users_get_all and ruta_ticketsentidades_get_all in session.get('permissions', []):
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
        response_tickets = api_client.get_data(ruta_tickets_get_all) # principal
        response_users = api_client.get_data(ruta_users_get_all)      # rutas adicionales  
        response_ticketsentidades = api_client.get_data(ruta_ticketsentidades_get_all)   # rutas adicionales

        # obtener rta de la api para la consulta principal
        if response_tickets['status'] == 'success':
            data_tickets = response_tickets['data']  # Extrae la lista de tickets
            message = f"{session['username']}: listado de tickets obtenido!"
        else:
            message = f"Error en la respuesta de la API (tickets): {response_tickets.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_tickets = []  # Asegúrate de pasar una lista vacía en caso de error

        # obtener rta de la api para la consulta adicional
        if response_users['status'] == 'success':
            data_users = response_users['data']  # Extrae la lista de usuarios
            message += f" y usuarios obtenidos!"
        else:
            message += f"Error en la respuesta de la API (usuarios): {response_users.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_users = []  # Asegúrate de pasar una lista vacía en caso de error
        
        # obtener rta de la api para la consulta adicional
        if response_ticketsentidades['status'] == 'success':
            data_ticketsentidades = response_ticketsentidades['data']  # Extrae la lista de tickets entidades
            message += f" y tickets entidades obtenidos!"
        else:
            message += f"Error en la respuesta de la API (ticketsentidades): {response_ticketsentidades.get('message', 'Error desconocido')}"
            flash(message, 'danger')
            data_ticketsentidades = []  # Asegúrate de pasar una lista vacía en caso de error


        # Crear un diccionario para mapear 
        users_dict = {user['id_user']: user['username'] for user in data_users}
        ticketsentidades_dict = {ticketentidad['id_ticket_entidad']: ticketentidad['table_fk'] for ticketentidad in data_ticketsentidades}

        # Agregar cada dato necesario y renombrar las claves
        renamed_tickets = []
        for ticket in data_tickets:
            ticket['username'] = users_dict.get(ticket['id_user_generator'], "")  # Si no se encuentra el id
            ticket['table_fk'] = ticketsentidades_dict.get(ticket['id_table_fk'], "") # Si no se encuentra el id
            renamed_ticket = {
                "ID": ticket['id_ticket'],
                "Entidad": ticket['table_fk'],
                "Creado por:": users_dict.get(ticket.get('id_user_generator'), ""),
                "Fecha y Hora de Creación": ticket['time_generated'],
                "Resuelto por:": users_dict.get(ticket.get('id_user_solver'), "-"),
                "Fecha y Hora de Resolución": ticket.get('time_solver', "-"),
                #"Acciones": f'<a href="{url_for("users.user_detail", user_id=user["id_user"])}" class="btn btn-primary">Ver</a>'
                "Acciones": f'<a href="#" class="btn btn-primary">Ver más</a>' '&nbsp;' 
                            # f'<a href="#" class="btn btn-primary">Block</a>' '&nbsp;' 
                            f'<a href="#" class="btn btn-primary">Editar</a>'
            }
            renamed_tickets.append(renamed_ticket)

        data = renamed_tickets
        flash(message, 'success')
    except requests.RequestException as e:
        message = f"Error obteniendo listado de tickets: {str(e)}"
        flash(message, 'danger')
        data = []

    return render_template('tickets_view.html', data=data, headers=headers)
















# @tickets_bp.route('/tickets/get/pendientes', methods=['GET'])
# def tickets_get_pendientes():
#         message = ''
    
#         # Encabezados para el render
#         headers = {
#             "app": Config.APP_TITLE,
#             "section": "Tickets Pendientes"
#         }
       
#         api_client = current_app.api_client
#         data = {}
#         try:
#             data = api_client.get_data('/tickets/get/pendientes')
#             if data:
#                 message = f"{session['username']}: listado de tickets pendientes obtenido!" ## chequear como poner esto! lo del username, va?
        
#             flash(message, 'success')
#         except requests.RequestException as e:
#             message = f"Error obteniendo listado de tickets pendientes: {str(e)}"
#             flash(message, 'danger')

#         return render_template('tickets_pendientes_view.html', data=data, headers=headers)

# @tickets_bp.route('/tickets/get/resueltos', methods=['GET'])
# def tickets_get_resueltos():
#         message = ''
    
#         # Encabezados para el render
#         headers = {
#             "app": Config.APP_TITLE,
#             "section": "Tickets Resueltos"
#         }
       
#         api_client = current_app.api_client
#         data = {}
#         try:
#             data = api_client.get_data('/tickets/get/resueltos')
#             if data:
#                 message = f"{session['username']}: listado de tickets resueltos obtenido!" ## chequear como poner esto! lo del username, va?
        
#             flash(message, 'success')
#         except requests.RequestException as e:
#             message = f"Error obteniendo listado de tickets resueltos: {str(e)}"
#             flash(message, 'danger')

#         return render_template('tickets_resueltos_view.html', data=data, headers=headers)