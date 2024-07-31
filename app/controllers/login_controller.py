# app/controllers/login.py

import datetime
from flask import Blueprint, current_app, flash,redirect, render_template, request, session, url_for
import jwt
import pytz
import requests
from app.config import Config


login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET','POST'])
def login():
    message=''
    
    #encabezados para el render
    headers = {
        "app": Config.APP_TITLE,
        "section":"Login"
    }
    
    if request.method == 'POST':
        username = request.form['username']
        usernumdoc = request.form['usernumdoc']
        password = request.form['password']
        api_client = current_app.api_client
        try:
            #autenticación
            # obtener el token
            api_client.authenticate(username, usernumdoc, password)
            token = api_client.token
            decoded_token = jwt.decode(token, options={"verify_signature": False})

            # guardar session
            session['username'] = decoded_token['username']
            session['permissions'] = decoded_token['permissions']
            session['role'] = decoded_token['role']
            
            message = f'{session['username']} iniciaste sesión!'
            flash(message, 'success')
            
            return redirect(url_for('index.index'))
            
        except requests.HTTPError as e:
            error_response = e.response.json()
            message = error_response.get('message', 'Las credenciales no son correctas! (panel)')
            flash(message, 'warning')

    return render_template('login.html', headers=headers)


@login_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Limpiar la sesión
    print("Logout",session['username'])
    session.clear()
    return redirect(url_for('login.login'))