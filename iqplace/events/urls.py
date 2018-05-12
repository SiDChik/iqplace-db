from sanic import Blueprint

from iqplace.events import views

events_blueprint = Blueprint('events', url_prefix='/api/events')

events_blueprint.add_route(views.create, '/create', methods=['POST'])
events_blueprint.add_route(views.get_list, '/', methods=['GET'])


