from supabase import create_client, Client

# Conectar ao Supabase
SUPABASE_URL = "https://zfqhryctnzysdndihfjg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpmcWhyeWN0bnp5c2RuZGloZmpnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkwNDI3MjEsImV4cCI6MjA2NDYxODcyMX0.vv1v29D0TOo7RfSBcJxKCTs3swFGNj6lSQ0eDDvRDcA"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)