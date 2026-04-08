# src/utils/parsers.py
import math

def parse_tw_int(val) -> int:
    if val is None: 
        return 0
    if isinstance(val, (int, float)): 
        return int(val)
    parsed = str(val).replace(',', '').replace('+', '').strip()
    return int(parsed) if parsed else 0
    
def parse_tw_float(val) -> float:
    if val is None: 
        return 0.0
    if isinstance(val, (int, float)): 
        return float(val)
    parsed = str(val).replace('%', '').replace(',', '').replace('+', '').strip()
    return float(parsed) if parsed else 0.0

def clean_nan(obj):
    """
    Recursively replaces NaN with None for valid JSON serialization.
    """
    if isinstance(obj, dict): 
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list): 
        return [clean_nan(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj): 
        return None
    return obj
