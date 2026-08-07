from chalicelib.routes.admin import trigger_sync_handler, get_logs_handler
from chalicelib.routes.skin_data import get_item_master_handler
from chalicelib.routes.auth import get_auth_config_handler

def register_all_routes(app):
    @app.route('/events/sync', methods=['POST'], cors=True)
    def trigger_sync():
        return trigger_sync_handler(app)

    @app.route('/logs', methods=['GET'], cors=True)
    def get_logs():
        return get_logs_handler()

    @app.route('/config', methods=['GET'], cors=True)
    def get_config():
        return get_auth_config_handler()

    @app.route('/skin-data/items', methods=['GET'], cors=True)
    def get_items():
        return get_item_master_handler()
