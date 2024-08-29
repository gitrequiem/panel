# app/controllers/reportes_controller.py

# Rutas
# ruta_reportes_simple = '/reportes/simple/post'
# ruta_reportes_promedio_tiempo_qx_plantas= '/reportes/promediotiempoqx/post'
# ruta_reportes_cx_especialidad_plantas = '/reportes/cxporespecialidad/post'
# ruta_reportes_cx_por_plantas = '/reportes/cxporplantas/post'
# ruta_reportes_suspensiones_por_plantas = '/reportes/suspensionesporplantas/post'
# ruta_reportes_complejidad_cx_realizadas_planta = '/reportes/complejidadcxrealizadas/post'
# ruta_reportes_nacionalidad_procedencia_plantas = '/reportes/nacionalidad/procedencia/post'
# ruta_reportes_promedio_tiempo_qx_urgencias = '/reportes/promediotiempoqx/urgencias/post'
# ruta_reportes_cx_especialidad_urgencias = '/reportes/cxporespecialidad/urgencias/post'
# ruta_reportes_complejidad_cx_realizadas_urgencias = '/reportes/complejidadcxrealizadas/urgencias/post'
# ruta_reportes_nacionalidad_procedencia_urgencias = '/reportes/nacionalidad/procedencia/urgencias/post'

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
        'ruta': '/reportes/cxporespecialidad/post',
        'titulo': 'Cirugías por Especialidad Planta'
    },
    'reporte_4':{
        'ruta': '/reportes/cxporplantas/post',
        'titulo': 'Cirugías por Plantas'
    },
    'reporte_5':{
        'ruta':'/reportes/suspensionesporplantas/post',
        'titulo': 'Suspensiones por Plantas'
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