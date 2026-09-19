# AI Tech Radar — Free MVP

Pipeline:

RSS / Hacker News API
→ Python
→ Gemini phân loại + tóm tắt
→ Supabase PostgreSQL
→ GitHub Actions
→ Telegram Daily Digest

## Chạy local

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Điền `.env`, sau đó:

```powershell
python scripts/test_connections.py
python collect.py
python digest.py
```

## GitHub Secrets cần tạo

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`
- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Lịch

- Collector: phút 17, mỗi 4 giờ, timezone `Asia/Ho_Chi_Minh`
- Daily Digest: 07:30 mỗi ngày, timezone `Asia/Ho_Chi_Minh`

## Bảo mật

Không commit `.env`.
Không đưa service-role key hoặc bot token vào frontend/public repo.
