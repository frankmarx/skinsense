import os
import requests
from typing import List, Optional
from chalicelib.connectors.csfloat.schemas import Listing, ListingDetail

# Configuration
CSFLOAT_API_URL = "https://csfloat.com/api/v1/listings"
CSFLOAT_PRICE_LIST_URL = "https://csfloat.com/api/v1/listings/price-list"
CSFLOAT_API_KEY = os.environ.get('CSFLOAT_API_KEY')

def get_item_listings() -> List[Listing]:
    """
    Retrieves the global price list for items from CSFloat.
    Maps raw JSON to Listing objects.
    """
    if not CSFLOAT_API_KEY:
        raise ValueError("CSFLOAT_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"ApiKey {CSFLOAT_API_KEY}",
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
    if not CSFLOAT_API_KEY:
        raise ValueError("CSFLOAT_API_KEY environment variable is not set.")

    all_listings = []
    cursor = None
    
    headers = {
        "Authorization": f"ApiKey {CSFLOAT_API_KEY}",
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
            response = requests.get(CSFLOAT_API_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            listings_data = data.get("listings", [])
            # Map raw dictionary to ListingDetail object
            all_listings.extend([ListingDetail(**l) for l in listings_data])
            
            cursor = data.get("cursor")
            if not cursor:
                break
                
        except Exception as e:
            print(f"Error fetching listings from CSFloat: {e}")
            break

    return all_listings
