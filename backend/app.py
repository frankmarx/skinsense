from chalice import Chalice, Response, CORSConfig
from dotenv import load_dotenv
import os
import requests
from chalicelib.db import get_db, init_db
from chalicelib.models import Price
from sqlalchemy import select

# Load .env from the backend directory and override existing environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

app = Chalice(app_name='skinsense-backend')

# Apply CORS config to allow frontend access
app.api.cors = CORSConfig(
    allow_origin='*', # Adjusted for simplicity, can be 'http://localhost:3000'
    allow_headers=['Content-Type', 'Authorization'],
    allow_credentials=True
)

# Initialize database tables
init_db()

CSGO_BACKPACK_API_URL = "https://csgobackpack.net/api/GetItemsList/v2/"

@app.schedule('rate(12 hours)')
def fetch_and_update_prices(event):
    """
    Scheduled task to fetch and update CS2 skin prices.
    """
    app.log.info("Starting scheduled task: fetch_and_update_prices")
    
    try:
        response = requests.get(CSGO_BACKPACK_API_URL, params={"currency": "USD"})
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            app.log.error("CSGOBackpack API returned success=False")
            return {"status": "error", "message": "API returned failure response"}
        
        items = data.get("items", {})
        
        with get_db() as db:
            for item_name, item_info in items.items():
                # Boilerplate Parsing Logic
                # prices_dict = item_info.get("price", {})
                # price_7d = prices_dict.get("7d", {}) if prices_dict else {}
                # average_price = price_7d.get("average", 0.0) if price_7d else 0.0
                
                # Example value for boilerplate:
                average_price = 0.0 
                
                # SQLAlchemy UPSERT pattern:
                # Check if item exists
                existing_item = db.query(Price).filter(Price.market_hash_name == item_name).first()
                if existing_item:
                    existing_item.price = average_price
                else:
                    db.add(Price(market_hash_name=item_name, price=average_price))
            
            db.commit()
            
        app.log.info("Database successfully updated with latest prices.")
        return {"status": "success", "message": "Prices successfully updated"}
        
    except Exception as e:
        app.log.error(f"Scheduled task failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.route('/prices', methods=['GET'], cors=True)
def get_prices():
    """
    Retrieves skin prices using SQLAlchemy. Returns dummy data if DB is empty or fails.
    """
    try:
        with get_db() as db:
            # Fetch items
            results = db.execute(select(Price)).scalars().all()
            
            if not results:
                app.log.info("Database prices table is empty. Returning dummy data.")
                return Response(body=get_dummy_data(), status_code=200, headers={"Content-Type": "application/json"})
            
            # Format data for JSON
            data = [
                {
                    "market_hash_name": item.market_hash_name,
                    "price": item.price,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None
                }
                for item in results
            ]
            
            return Response(body={"status": "success", "data": data}, status_code=200, headers={"Content-Type": "application/json"})
            
    except Exception as e:
        app.log.error(f"Error retrieving prices: {str(e)}")
        return Response(body=get_dummy_data(), status_code=200, headers={"Content-Type": "application/json"})

def get_dummy_data():
    """
    Generates dummy JSON data for local development.
    """
    return {
        "status": "success",
        "is_dummy": True,
        "data": [
            {"market_hash_name": "★ M9 Bayonet | Doppler (Factory New)", "price": 1420.50, "updated_at": "2026-05-24T12:00:00Z"},
            {"market_hash_name": "AK-47 | Case Hardened (Minimal Wear)", "price": 380.00, "updated_at": "2026-05-24T12:00:00Z"},
            {"market_hash_name": "AWP | Asiimov (Field-Tested)", "price": 165.25, "updated_at": "2026-05-24T12:00:00Z"},
            {"market_hash_name": "M4A1-S | Printstream (Field-Tested)", "price": 210.80, "updated_at": "2026-05-24T12:00:00Z"},
            {"market_hash_name": "★ Sport Gloves | Pandora's Box (Battle-Scarred)", "price": 890.00, "updated_at": "2026-05-24T12:00:00Z"},
            {"market_hash_name": "Glock-18 | Fade (Factory New)", "price": 1150.00, "updated_at": "2026-05-24T12:00:00Z"},
            {"market_hash_name": "Desert Eagle | Blaze (Factory New)", "price": 620.45, "updated_at": "2026-05-24T12:00:00Z"},
            {"market_hash_name": "★ Karambit | Marble Fade (Factory New)", "price": 1580.00, "updated_at": "2026-05-24T12:00:00Z"}
        ]
    }
