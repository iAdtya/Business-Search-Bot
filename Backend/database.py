import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if url is None or key is None:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the environment variables")

supabase: Client = create_client(supabase_url=url, supabase_key=key)