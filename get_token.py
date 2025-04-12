import requests

SUPABASE_URL = "https://ozftcqjtwtpmalmojnzp.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im96ZnRjcWp0d3RwbWFsbW9qbnpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3OTU0NjAsImV4cCI6MjA1OTM3MTQ2MH0.vv6WXXl7coOSfE5kkAHUs__cPK0t6VsY3eWmc2vak-A"
EMAIL = "test@example.com"
PASSWORD = "CR16retired!"

resp = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", json={
    "email": EMAIL,
    "password": PASSWORD
}, headers={
    "apikey": SUPABASE_API_KEY,
    "Content-Type": "application/json"
})

print(resp.json())
