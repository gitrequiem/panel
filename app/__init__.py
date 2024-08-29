# app/__init__.py
from flask import Flask
from app.config import Config
from app.api_client import APIClient

app = Flask(__name__)
app.config.from_object(Config)

# Configurar la clave secreta
app.secret_key = 'requiem.panel.2024'  # Reemplaza con una cadena aleatoria y segura

# initialize API client
api_client = APIClient(app.config['API_BASE_URL'])
app.api_client = api_client

# routes (blueprints)
from app.controllers.index_controller import index_bp
app.register_blueprint(index_bp)

from app.controllers.login_controller import login_bp
app.register_blueprint(login_bp)

from app.controllers.users_controller import users_bp
app.register_blueprint(users_bp)

from app.controllers.usersroles_controller import usersroles_bp
app.register_blueprint(usersroles_bp)

from app.controllers.userspermissions_controller import userspermissions_bp
app.register_blueprint(userspermissions_bp)

from app.controllers.pacientes_controller import pacientes_bp
app.register_blueprint(pacientes_bp)

from app.controllers.diagnosticos_controller import diagnosticos_bp
app.register_blueprint(diagnosticos_bp)

from app.controllers.intervenciones_controller import intervenciones_bp
app.register_blueprint(intervenciones_bp)

from app.controllers.finalizaciones_controller import finalizaciones_bp
app.register_blueprint(finalizaciones_bp)

from app.controllers.cirugias_controller import cirugias_bp
app.register_blueprint(cirugias_bp)

from app.controllers.staffs_controller import staffs_bp
app.register_blueprint(staffs_bp)

from app.controllers.staffs_tipos_controller import stafftipos_bp
app.register_blueprint(stafftipos_bp)

from app.controllers.tickets_controller import tickets_bp
app.register_blueprint(tickets_bp)

from app.controllers.reportes_controller import reportes_bp
app.register_blueprint(reportes_bp)

