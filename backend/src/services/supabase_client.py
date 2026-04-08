# src/services/supabase_client.py
import os
import json
from supabase import create_client, Client
from typing import Dict, Any

class SupabaseManager:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Client = None
        if self.url and self.key:
            self.client = create_client(self.url, self.key)

    def is_connected(self) -> bool:
        return self.client is not None

    def upsert_snapshot(self, table_name: str, payload: Dict[str, Any], limit: int = 1):
        """
        Inserts new snapshot and retains only the `limit` newest records.
        limit=1 means only latest snapshot.
        limit=180 means 180 snapshots for historical tracing.
        """
        if not self.is_connected():
            print("Supabase connection not found. Falling back to local file.")
            self._save_local(table_name, payload)
            return

        try:
            # Insert the new snapshot
            self.client.table(table_name).insert({"data": payload}).execute()
            print(f"Successfully uploaded to {table_name}")

            # Garbage Collection
            if limit > 0:
                res = self.client.table(table_name).select("id").order("created_at", desc=True).execute()
                if res.data and len(res.data) > limit:
                    # Collect all ids older than `limit`
                    ids_to_del = [x['id'] for x in res.data[limit:]]
                    for idx in ids_to_del:
                        self.client.table(table_name).delete().eq("id", idx).execute()
                    print(f"Deleted {len(ids_to_del)} old records to maintain limit {limit}.")
        except Exception as e:
            print(f"Error uploading/GC to Supabase: {e}")
            self._save_local(table_name, payload)

    def _save_local(self, table_name: str, payload: Dict[str, Any]):
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'public'))
        if not os.path.exists(out_dir): 
            os.makedirs(out_dir)
            
        file_name = 'data.json' if table_name == 'market_snapshots' else 'tw_data.json'
        out_file = os.path.join(out_dir, file_name)
        
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Saved locally to {out_file}")
