import os
import json

def clear_data():
    local_path = "frontend/public/tw_data.json"
    if os.path.exists(local_path):
        os.remove(local_path)
        print("Deleted local tw_data.json")
    
    try:
        from supabase import create_client, Client
        from dotenv import load_dotenv
        
        load_dotenv("backend/.env")
        load_dotenv("frontend/.env")

        url = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")
        
        if url and key:
            supabase: Client = create_client(url, key)
            res = supabase.table("tw_market_snapshots").select("id").execute()
            if res.data:
                for row in res.data:
                    supabase.table("tw_market_snapshots").delete().eq("id", row["id"]).execute()
                print(f"Deleted {len(res.data)} rows from Supabase.")
        else:
            print("No Supabase keys found for clearing.")
    except Exception as e:
        print("Error clearing Supabase:", e)

if __name__ == "__main__":
    clear_data()
