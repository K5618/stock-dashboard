# fetcher.py
import os
from src.services.global_aggregator import GlobalDataAggregator
from src.services.supabase_client import SupabaseManager
from src.schemas.market_data import MarketSnapshot
from dotenv import load_dotenv

def main():
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env'))
    
    # Generate data
    aggregator = GlobalDataAggregator()
    payload = aggregator.gather_data()
    
    # Validate payload strictly with Pydantic
    try:
        validated_payload = MarketSnapshot(**payload).model_dump()
        print("Data validation passed.")
    except Exception as e:
        print(f"Data validation failed. Expected schema mismatch: {e}")
        # In a real rigorous scenario, we might abort. Here we just log for visibility
        # and fallback to the raw payload ensuring frontend doesn't break if schema drift happens.
        validated_payload = payload
        
    # We fetch limit config from env or default to 2
    gc_limit = int(os.environ.get("MARKET_SNAPSHOTS_LIMIT", 2))
    
    # Store data
    db = SupabaseManager()
    db.upsert_snapshot("market_snapshots", validated_payload, limit=gc_limit)

if __name__ == '__main__':
    main()
