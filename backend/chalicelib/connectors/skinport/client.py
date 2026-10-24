import requests
from typing import List, Optional
from chalicelib.connectors.skinport.schemas import SalesHistoryEntry, Item

# Configuration
SKINPORT_API_URL = "https://api.skinport.com/v1"
SKINPORT_SALES_HISTORY_URL = f"{SKINPORT_API_URL}/sales/history"
SKINPORT_ITEMS_URL = f"{SKINPORT_API_URL}/items"

def _request(url, params):
    """
    Issues a GET request to a SkinPort endpoint and returns the parsed JSON.

    No authorization required. Endpoints are rate limited to 8 requests per
    5 minutes and cached server-side for 5 minutes. The 'Accept-Encoding: br'
    header is required (Brotli compression).

    Raises:
        requests.HTTPError: On a non-2xx response.
        requests.RequestException: On connection failures.
    """
    headers = {
        "Accept-Encoding": "br",
        "User-Agent": "Skinsense-Price-Aggregator/1.0"
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def get_sales_history(market_hash_name: Optional[str] = None, app_id: int = 730, currency: str = "USD") -> List[SalesHistoryEntry]:
    """
    Retrieves aggregated sales history for items sold on SkinPort.
    Maps raw JSON to SalesHistoryEntry objects.

    Args:
        market_hash_name: Comma-delimited item names to filter on.
            Omit to fetch every item.
        app_id: The app id for the inventory's game (default 730, CS2).
        currency: Currency for pricing (default USD).

    Returns:
        List[SalesHistoryEntry]: One entry per item.
    """
    params = {"app_id": app_id, "currency": currency}
    if market_hash_name:
        params["market_hash_name"] = market_hash_name

    return [SalesHistoryEntry(**item) for item in _request(SKINPORT_SALES_HISTORY_URL, params)]

def get_items(app_id: int = 730, currency: str = "USD", tradable: bool = True) -> List[Item]:
    """
    Retrieves all items available on the SkinPort marketplace.
    Maps raw JSON to Item objects.

    Args:
        app_id: The app id for the inventory's game (default 730, CS2).
        currency: Currency for pricing (default USD).
        tradable: If True, only tradable items are returned (default True).

    Returns:
        List[Item]: One entry per item.
    """
    params = {
        "app_id": app_id,
        "currency": currency,
        "tradable": "true" if tradable else "false",
    }

    return [Item(**item) for item in _request(SKINPORT_ITEMS_URL, params)]


def test_connection():
    """
    Tests the connection to the SkinPort API by hitting the items endpoint.
    """
    headers = {
        "Accept-Encoding": "br",
        "User-Agent": "Skinsense-Price-Aggregator/1.0"
    }

    try:
        response = requests.get(SKINPORT_ITEMS_URL, headers=headers)
        response.raise_for_status()
        return {"status": "success", "status_code": response.status_code}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
