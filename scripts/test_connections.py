import os
import socket
from datetime import datetime, timezone

import requests
import urllib3.util.connection as urllib3_cn

from google import genai
from supabase import create_client
from dotenv import load_dotenv


urllib3_cn.allowed_gai_family = lambda: socket.AF_INET

load_dotenv()

print("=== 1. Test Gemini ===")
gemini_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
client = genai.Client(api_key=gemini_key)
response = client.interactions.create(
    model=model,
    input="Trả lời đúng một câu: Gemini connection OK",
)
print(response.output_text)

print("\n=== 2. Test Supabase ===")
sb = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SECRET_KEY"),
)
result = sb.table("articles").select("id").limit(1).execute()
print("Supabase connection OK. Rows sample:", len(result.data or []))

print("\n=== 3. Test Telegram ===")
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
resp = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={
        "chat_id": chat_id,
        "text": f"✅ AI Tech Radar kết nối thành công lúc {datetime.now(timezone.utc).isoformat()}",
    },
    timeout=30,
)
resp.raise_for_status()
print("Telegram connection OK.")
