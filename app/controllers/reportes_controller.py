# app/controllers/reportes_controller.py

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import requests
from app.config import Config

reportes_bp = Blueprint('reportes', __name__)

# Diccionario de Reportes
reportes_dict={
    'reporte_1':{
         'ruta':'/reportes/simple/post',
         'titulo':'Reporte Simple' 
    },
    'reporte_2':{
        'ruta': '/reportes/promediotiempoqx/post',
        'titulo': 'Promedio Tiempo Quirúrgico Plantas'
        
    },
    'reporte_3':{
        'ruta': '/reporte/cxporespecialidad/post',
        'titulo': 'Cirugías por Especialidad Planta'
    },
    'reporte_4':{
        'ruta': '/reportes/cxporplantas/post',
        'titulo': 'Cirugías por plantas'
    },
    'reporte_5':{
        'ruta':'/reportes/suspensionesporplantas/post',
        'titulo': 'Suspensiones por plantas'
    },
    'reporte_6':{
        'ruta': '/reportes/complejidadcxrealizadas/post',
        'titulo':'Complejidad Cirugías Realizadas Planta'
    },
    'reporte_7':{
        'ruta':'/reportes/nacionalidad/procedencia/post',
        'titulo':'Nacionaliad-Procedencia Planta'
    },
    'reporte_8':{
        'ruta':'/reportes/promediotiempoqx/urgencias/post',
        'titulo': 'Promedio Tiempo Quirúrgico Urgencias'
    },
    'reporte_9':{
        'ruta': '/reportes/cxporespecialidad/urgencias/post',
        'titulo':'Cirugías por Especialidad Urgencias'
    },
    'reporte_10':{
        'ruta':'/reportes/complejidadcxrealizadas/urgencias/post',
        'titulo':'Complejidad Cirugías Realizadas Urgencias'
    },
    'reporte_11':{
        'ruta':'/reportes/nacionalidad/procedencia/urgencias/post',
        'titulo':'Nacionaliad-Procedencia Urgencias'
    } 
}

# Rutas
# ruta_reportes_simple = '/reportes/simple/post'
# ruta_reportes_promedio_tiempo_qx_plantas= '/reportes/promediotiempoqx/post'
# ruta_reportes_cx_especialidad_plantas = '/reporte/cxporespecialidad/post'
# ruta_reportes_cx_por_plantas = '/reportes/cxporplantas/post'
# ruta_reportes_suspensiones_por_plantas = '/reportes/suspensionesporplantas/post'
# ruta_reportes_complejidad_cx_realizadas_planta = '/reportes/complejidadcxrealizadas/post'
# ruta_reportes_nacionalidad_procedencia_plantas = '/reportes/nacionalidad/procedencia/post'
# ruta_reportes_promedio_tiempo_qx_urgencias = '/reportes/promediotiempoqx/urgencias/post'
# ruta_reportes_cx_especialidad_urgencias = '/reportes/cxporespecialidad/urgencias/post'
# ruta_reportes_complejidad_cx_realizadas_urgencias = '/reportes/complejidadcxrealizadas/urgencias/post'
# ruta_reportes_nacionalidad_procedencia_urgencias = '/reportes/nacionalidad/procedencia/urgencias/post'

# @reportes_bp('/reportes', Method=['GET','POST'])
# def reportes_all():
#     message = ''
    
#     headers = {
#         "app": Config.APP_TITLE,
#         "section": "Reportes"
#     }
#     # permisos
#     authorized = False
#     if ruta_reportes_simple and ruta_reportes_promedio_tiempo_qx_plantas and ruta_reportes_cx_especialidad_plantas and ruta_reportes_cx_por_plantas and ruta_reportes_suspensiones_por_plantas and ruta_reportes_complejidad_cx_realizadas_planta and ruta_reportes_nacionalidad_procedencia_plantas and ruta_reportes_promedio_tiempo_qx_urgencias and ruta_reportes_cx_especialidad_urgencias and ruta_reportes_complejidad_cx_realizadas_urgencias and ruta_reportes_nacionalidad_procedencia_urgencias in session.get('permissions', []):
#         authorized = True
        
#     if not authorized:
#         message = f"Usuario no autorizado (permissions err)"
#         flash(message, 'warning')
#         return redirect(url_for('index.index'))
    
#     # Crear un diccionario para mapear id_role a role name
#     rutas_reportes = {datos['ruta']: titulo for titulo, datos in reportes_dict.items()}
    
#     if request.method == 'POST':
#         data = {
#             'Desde': request.form['start_date'], #fecha desde
#             'Hasta': request.form['end_date'], #fecha hasta
#             'Reporte': request.form['titulo'], #reporte con el nombre que le de yo a la ruta despues
            
#         }
#         try:
#             api_client = current_app.api_client
#             response = api_client.post_data(rutas_reportes, data) # request.form del reporte que elige el usuario, y en data le paso el start date y el end date, los ahi en data
#             if response['status'] == 'success':                     # para la linea de arriba: en donde esta la ruta le paso el selector de la ruta que quiero el informe
#                 flash('Reporte obtenido!', 'success')
#                 return redirect(url_for('reportes.reportes_all'))
#             else:
#                 flash(f"Error al pedir el eporte: {response.get('message', 'Error desconocido')}", 'danger')
#         except requests.RequestException as e:
#             flash(f"Error al comunicarse con la API: {str(e)}", 'danger')
#     api_client = current_app.api_client
#     return render_template('reportes_form.html', headers=headers, form_action=url_for('reportes.reportes_all'))

# @reportes_bp.route('/reportes', methods=['GET', 'POST'])
# def reportes_all():
#     message = ''
#     headers = {"app": Config.APP_TITLE, "section": "Reportes"}

#     # Verificar permisos
#     authorized = set(session.get('permissions', []))
#     if not authorized:
#         message = f"Usuario no autorizado (permissions err)"
#         flash(message, 'warning')
#         return redirect(url_for('index.index'))

#     # Opciones para el formulario
#     opciones_reportes = [(k, v['titulo']) for k, v in reportes_dict.items()]

#     if request.method == 'POST':
#         data = {
#             'Desde': request.form['start_date'],
#             'Hasta': request.form['end_date'],
#             'Reporte': request.form['titulo'],
#         }
#         try:
#             api_client = current_app.api_client
#             ruta = reportes_dict[data['Reporte']]['ruta']  # Obtener la ruta del reporte seleccionado
#             response = api_client.post_data(ruta, data)
#             if response['status'] == 'success':
#                 flash('Reporte obtenido!', 'success')
#             else:
#                 flash(f"Error al pedir el eporte: {response.get('message', 'Error desconocido')}", 'danger')
#         except requests.RequestException as e:
#             flash(f"Error al comunicarse con la API: {str(e)}", 'danger')
            
#     api_client = current_app.api_client
#     return render_template('reportes_form.html', headers=headers, 
#                            opciones=opciones_reportes, form_action=url_for('reportes.reportes_all'))


@reportes_bp.route('/reportes', methods=['GET', 'POST'])
def reportes_all():
    message = ''
    headers = {"app": Config.APP_TITLE, "section": "Reportes"}

    # Verificar permisos
    authorized = set(session.get('permissions', []))
    if not authorized:
        message = f"Usuario no autorizado (permissions err)"
        flash(message, 'warning')
        return redirect(url_for('index.index'))

    # Opciones para el formulario
    #opciones_reportes = [  (k['titulo'], v['ruta']   ) for k, v in reportes_dict.items()]
    opciones_reportes = [   [reporte['titulo'], reporte['ruta']] for reporte in reportes_dict.values()    ]

    print(opciones_reportes)
    
    if request.method == 'POST':
        #preparo la data del json para el post_data
        data = {
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date']
            }
        #preparo el endpoint para el post_data
        url_reporte_seleccionado = request.form['url_reporte']
        
        try:
            #instancia api_client
            api_client = current_app.api_client
            #armo el request
            response = api_client.post_data(url_reporte_seleccionado, data)
            print(response)
            if response['status'] == 'success':
                flash('Reporte obtenido!', 'success')
            else:
                flash(f"Error al pedir el eporte: {response.get('message', 'Error desconocido')}", 'danger')
        except requests.RequestException as e:
            flash(f"Error al comunicarse con la API: {str(e)}", 'danger')

    api_client = current_app.api_client
    return render_template('reportes_form.html', 
                           headers=headers, 
                           opciones=opciones_reportes, 
                           form_action=url_for('reportes.reportes_all'))