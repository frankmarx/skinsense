from .administration import trigger_sync_logic, get_logs_logic

def register_admin_routes(app):
    @app.route('/events/sync', methods=['POST'], cors=True)
    def trigger_sync():
        data = app.current_request.json_body
        action = data.get('action', 'cs_float_item_listings')
        return trigger_sync_logic(action=action)

    @app.route('/logs', methods=['GET'], cors=True)
    def get_logs():
        return get_logs_logic()

