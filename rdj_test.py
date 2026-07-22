import sys, os
sys.path.insert(0, "/app")
os.chdir("/app")
from config.settings import DATABASE_CONFIG
cfg = DATABASE_CONFIG.get("radiodj", {})
print("api_url:", cfg.get("api_url"))
print("api_key:", cfg.get("api_key"))
import requests
url = cfg.get("api_url", "").rstrip("/") + "/opt"
params = {"command": "Status", "auth": cfg.get("api_key", "")}
print("requesting:", url, params)
try:
    r = requests.get(url, params=params, timeout=5)
    print("status:", r.status_code)
    r.raise_for_status()
    print("body:", r.text[:200])
    print("RESULT: not None =", r.text is not None)
except Exception as e:
    print("error:", type(e).__name__, e)

# Also test validate_connection directly
print("\n--- validate_connection ---")
from src.radiodj_integration.radiodj_client import radiodj_client
result = radiodj_client.validate_connection()
print("result:", result)
