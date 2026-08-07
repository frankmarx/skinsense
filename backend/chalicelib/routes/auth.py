from chalice import Response
from chalicelib.utils.config import get_cognito_client_id, get_cognito_user_pool_id

def get_auth_config_handler():
    return Response(
        body={
            "cognito_client_id": get_cognito_client_id(),
            "cognito_user_pool_id": get_cognito_user_pool_id(),
        },
        status_code=200,
        headers={"Content-Type": "application/json"}
    )
