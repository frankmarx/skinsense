import requests
from typing import List, Optional
from chalicelib.connectors.skinport.schemas import SalesHistoryEntry

# Configuration
SKINPORT_API_URL = "https://api.skinport.com/v1"
SKINPORT_SALES_HISTORY_URL = f"{SKINPORT_API_URL}/sales/history"

def get_sales_history(market_hash_name: Optional[str] = None, app_id: int = 730, currency: str = "USD") -> List[SalesHistoryEntry]:
    """
    Retrieves aggregated sales history for items sold on SkinPort.
    Maps raw JSON to SalesHistoryEntry objects.

    No authorization required. Rate limited to 8 requests per 5 minutes and
    cached server-side for 5 minutes. The 'Accept-Encoding: br' header is
    required by this endpoint (Brotli compression).

    Args:
        market_hash_name: Comma-delimited item names to filter on.
            Omit to fetch every item.
        app_id: The app id for the inventory's game (default 730, CS2).
        currency: Currency for pricing (default USD).

    Returns:
        List[SalesHistoryEntry]: One entry per item.

    Raises:
        requests.HTTPError: On a non-2xx response.
        requests.RequestException: On connection failures.
    """
    params = {"app_id": app_id, "currency": currency}
    if market_hash_name:
        params["market_hash_name"] = market_hash_name

    headers = {
        "Accept-Encoding": "br",
        "User-Agent": "Skinsense-Price-Aggregator/1.0"
    }

    response = requests.get(SKINPORT_SALES_HISTORY_URL, params=params, headers=headers)
    response.raise_for_status()
    return [SalesHistoryEntry(**item) for item in response.json()]
