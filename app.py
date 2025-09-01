
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from db import init_db
from handlers.user import register as register_user
from handlers.admin import register as register_admin

def main():
    init_db()
    app = Client("join-check-bot-pro-buttons", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    register_user(app)
    register_admin(app)
    app.run()

if __name__ == "__main__":
    main()
