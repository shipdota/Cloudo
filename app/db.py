import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "http://localhost:54321")
# Dummy JWT for testing so create_client doesn't fail on missing/invalid JWT format
dummy_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlc3QiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYxNjQxNzMwOSwiZXhwIjoxOTMyMDE3MzA5fQ.test"
key: str = os.environ.get("SUPABASE_KEY", dummy_jwt)

supabase: Client = create_client(url, key)

def get_db():
    return supabase
