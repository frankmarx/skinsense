import json
import requests
from typing import List, Optional
from chalicelib.connectors.csfloat.schemas import Listing, ListingDetail
from chalicelib.utils.config import get_csfloat_api_key

# Configuration
CSFLOAT_BASE_URL = "https://csfloat.com/api/v1"
CSFLOAT_LISTINGS_URL = f"{CSFLOAT_BASE_URL}/listings"
CSFLOAT_PRICE_LIST_URL = f"{CSFLOAT_LISTINGS_URL}/price-list"

def fetch_endpoint(endpoint: str, params: Optional[dict] = None) -> dict:
    """
    Makes a GET request to an arbitrary CSFloat API endpoint and prints the JSON response.
    `endpoint` is a path relative to the CSFloat API base, e.g. "listings" or "listings/price-list".
    """
    api_key = get_csfloat_api_key()
    if not api_key:
        raise ValueError("CSFLOAT_API_KEY environment variable or secret is not set.")

    url = f"{CSFLOAT_BASE_URL}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": api_key,
        "User-Agent": "Skinsense-Price-Aggregator/1.0"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(json.dumps(data, indent=2))
    return data

def get_item_listings() -> List[Listing]:
    """
    Retrieves the global price list for items from CSFloat.
    Maps raw JSON to Listing objects.
    """
    api_key = get_csfloat_api_key()
    if not api_key:
        raise ValueError("CSFLOAT_API_KEY environment variable or secret is not set.")

    headers = {
        "Authorization": api_key,
        "User-Agent": "Skinsense-Price-Aggregator/1.0"
    }

    try:
        response = requests.get(CSFLOAT_PRICE_LIST_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Assuming the price-list endpoint returns a list of items directly
        # or a dictionary containing the list in a key.
        items = data if isinstance(data, list) else data.get("items", [])
        
        return [Listing(**item) for item in items]
    except Exception as e:
        print(f"Error fetching price list from CSFloat: {e}")
        return []

def get_item_listing_details(market_hash_name: str) -> List[ListingDetail]:
    """
    Retrieves every active listing for a specific item from CSFloat.
    Maps raw JSON to ListingDetail objects.
    """
    api_key = get_csfloat_api_key()
    if not api_key:
        raise ValueError("CSFLOAT_API_KEY environment variable or secret is not set.")

    all_listings = []
    cursor = None
    
    headers = {
        "Authorization": api_key,
        "User-Agent": "Skinsense-Price-Aggregator/1.0"
    }

    while True:
        params = {
            "market_hash_name": market_hash_name,
            "limit": 50
        }
        if cursor:
            params["cursor"] = cursor

        try:
            response = requests.get(CSFLOAT_LISTINGS_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            listings_data = data.get("data", [])
            # Map raw dictionary to ListingDetail object
            all_listings.extend([ListingDetail(**l) for l in listings_data])
            
            cursor = data.get("cursor")
            if not cursor:
                break
                
        except Exception as e:
            print(f"Error fetching listings from CSFloat: {e}")
            break

    return all_listings


def test_connection():
    """
    Tests the connection to the CSFloat API by hitting the price-list endpoint.
    """
    api_key = get_csfloat_api_key()
    if not api_key:
        return {"status": "error", "message": "API Key not set"}

    headers = {
        "Authorization": api_key,
        "User-Agent": "Skinsense-Price-Aggregator/1.0"
    }

    try:
        response = requests.get(CSFLOAT_PRICE_LIST_URL, headers=headers)
        response.raise_for_status()
        return {"status": "success", "status_code": response.status_code}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import os
    import sys
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

    usage = (
        "Usage: python -m chalicelib.connectors.csfloat.client <endpoint> [key=value ...]\n"
        "  e.g. python -m chalicelib.connectors.csfloat.client listings 'market_hash_name=AK-47 | Redline (Field-Tested)' limit=5"
    )
    if len(sys.argv) < 2:
        print(usage, file=sys.stderr)
        sys.exit(2)

    endpoint = sys.argv[1]
    params = {}
    for arg in sys.argv[2:]:
        key, sep, value = arg.partition("=")
        if not sep:
            print(f"Invalid param {arg!r}, expected key=value", file=sys.stderr)
            sys.exit(2)
        params[key] = value

    try:
        fetch_endpoint(endpoint, params=params or None)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
