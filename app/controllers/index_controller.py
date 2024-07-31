# app/controllers/index.py

from flask import Blueprint, jsonify, redirect, render_template, session, url_for
from app.config import Config

index_bp = Blueprint('index', __name__)

@index_bp.route('/', methods=['GET'])
def index():
    url = Config.API_BASE_URL
    
    # response = requests.post(f'{url}/login', json={
    #         'username': 'admin',
    #         'usernumdoc': '00000000',
    #         'password': 'Admin.0000'
    #     })
    
    # json_response = response.json()
    # response.raise_for_status()
    # token = json_response.get('access_token')
    
    # if 'username' in session:
    #     username = session['username']
    #     permissions = session['permissions']
    #     role = session['role']
    #     exp = session['exp']
    #     exp_epoch=session['exp_epoch']
        
    #     # Utiliza los datos como sea necesario en tu lógica de aplicación
    #     return jsonify({'username':username, 'role':role, 'permissions':permissions, 'exp': exp, 'exp_epoch': exp_epoch})
    #encabezados para el render
    headers = {
        "app": Config.APP_TITLE,
        "section":"Home"
    }
    
    if session:
        #return render_template('index.html', headers=headers)
        return render_template('index.html', headers=headers)
    
    else:
        return redirect(url_for('login.login'))
    
    
    
    #return jsonify({'message':'Bienvenido a requiem!'}), 200