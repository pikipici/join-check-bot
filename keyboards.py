
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from i18n import t
from config import LOCALE, BUTTONS_PER_ROW

def admin_main_kb():
    rows = [
        [InlineKeyboardButton(t(LOCALE, "btn_list"), callback_data="adm:list")],
        [InlineKeyboardButton(t(LOCALE, "btn_add"), callback_data="adm:add")],
        [InlineKeyboardButton(t(LOCALE, "btn_del"), callback_data="adm:del")],
        [InlineKeyboardButton(t(LOCALE, "btn_setcontent"), callback_data="adm:setcontent")],
        [InlineKeyboardButton(t(LOCALE, "btn_setimg"), callback_data="adm:setimg")],
    ]
    return InlineKeyboardMarkup(rows)

def admin_back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(LOCALE, "btn_back"), callback_data="adm:back")]])

def build_delete_list(items: List, locale: str):
    # items are db.RequiredChat rows
    rows = []
    row = []
    for it in items:
        label = (it.label or it.chat)[:30]
        btn = InlineKeyboardButton(f"❌ {label}", callback_data=f"adm:delid:{it.id}")
        row.append(btn)
        if len(row) >= BUTTONS_PER_ROW:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(t(locale, "btn_back"), callback_data="adm:back")])
    return InlineKeyboardMarkup(rows)
