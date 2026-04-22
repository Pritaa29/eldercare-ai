import os
port = os.environ.get("PORT", "8080")
os.system(f"daphne -b 0.0.0.0 -p {port} eldercare.asgi:application")