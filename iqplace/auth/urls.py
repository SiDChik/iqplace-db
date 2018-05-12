from sanic import Blueprint

from iqplace.auth import views

auth_blueprint = Blueprint('auth', url_prefix='/api/auth')

auth_blueprint.add_route(views.login, '/login', methods=['POST'])
auth_blueprint.add_route(views.check_registration, '/check_registration', methods=['POST'])
auth_blueprint.add_route(views.registration, '/registration', methods=['POST'])
auth_blueprint.add_route(views.login_sms, '/login_sms', methods=['POST'])
auth_blueprint.add_route(views.login_social, '/login_social', methods=['POST'])


