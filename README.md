# Join-Check Bot PRO (Buttons + Modules + Postgres)

Modular & button-driven admin panel.

## Struktur
- `app.py` — entrypoint
- `config.py` — env & logging
- `db.py` — SQLAlchemy models & CRUD
- `i18n.py` — teks multi-bahasa (id/en)
- `keyboards.py` — tombol-tombol inline
- `handlers/user.py` — alur user (/start, Check ✅)
- `handlers/admin.py` — panel admin full tombol
- `wait_for_postgres.py` — tunggu DB
- `docker-compose.yml`, `Dockerfile`, `requirements.txt`
- `.env.sample`

## Jalankan
```bash
cp .env.sample .env
# edit API_ID, API_HASH, BOT_TOKEN, OWNER_ID/ADMINS
docker compose up -d --build
docker compose logs -f bot
```

## Admin Panel
Chat pribadi ke bot:
- `/admin` → tampilkan panel:
  - 📋 Daftar Wajib Join
  - ➕ Tambah Wajib Join (flow dengan balasan pesan)
  - 🗑 Hapus Wajib Join (pilih dari daftar tombol)
  - 🔗 Set CONTENT_URL
  - 🖼 Set START_IMAGE_URL
