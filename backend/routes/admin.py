from .administration import trigger_sync_logic, get_logs_logic

def register_admin_routes(app):
    @app.route('/events/sync', methods=['POST'], cors=True)
    def trigger_sync():
        return trigger_sync_logic()

    @app.route('/logs', methods=['GET'], cors=True)
    def get_logs():
        return get_logs_logic()

