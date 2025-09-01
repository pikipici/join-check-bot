
from typing import Dict, Any
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from config import ADMINS, LOCALE
from i18n import t
from keyboards import admin_main_kb, admin_back_kb, build_delete_list
from db import get_all_required, add_required, delete_required_by_id, get_setting, set_setting

ADMIN_STATE: Dict[int, Dict[str, Any]] = {}

def is_admin(uid: int) -> bool:
    return uid in ADMINS

def normalize_chat(s: str) -> str:
    s = (s or "").strip()
    if not s: return s
    for pref in ("https://t.me/", "http://t.me/", "t.me/"):
        if s.startswith(pref):
            s = s[len(pref):]
            break
    if s.startswith("+"):  # invite hash only
        return s
    if not s.startswith("@") and not s.startswith("-100"):
        s = "@" + s
    return s

def register(app: Client):
    @app.on_message(filters.command("admin") & filters.private)
    async def on_admin(client: Client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        if not is_admin(uid):
            return await message.reply_text(t(LOCALE, "admin_only"))
        await message.reply_text(t(LOCALE, "admin_title") + "\\n" + t(LOCALE, "admin_desc"), reply_markup=admin_main_kb())

    @app.on_callback_query(filters.regex("^adm:"))
    async def on_admin_cb(client: Client, cq: CallbackQuery):
        uid = cq.from_user.id
        if not is_admin(uid):
            return await cq.answer(t(LOCALE, "admin_only"), show_alert=True)

        data = cq.data  # e.g., adm:list / adm:add / adm:del / adm:setcontent / adm:setimg / adm:back
        if data == "adm:list":
            items = get_all_required()
            if not items:
                await cq.message.edit_text(t(LOCALE, "list_empty"), reply_markup=admin_back_kb())
            else:
                lines = [t(LOCALE, "list_header")]
                for i, it in enumerate(items, 1):
                    lines.append(f"{i}. {(it.label or it.chat)} ({it.chat}) — {it.url or '-'}")
                await cq.message.edit_text("\\n".join(lines), reply_markup=admin_back_kb())
            return await cq.answer()

        if data == "adm:del":
            items = get_all_required()
            if not items:
                await cq.message.edit_text(t(LOCALE, "list_empty"), reply_markup=admin_back_kb())
            else:
                await cq.message.edit_text(t(LOCALE, "del_pick"), reply_markup=build_delete_list(items, LOCALE))
            return await cq.answer()

        if data.startswith("adm:delid:"):
            try:
                dbid = int(data.split(":")[2])
            except Exception:
                return await cq.answer("bad id", show_alert=True)
            ok, label, chat = delete_required_by_id(dbid)
            if ok:
                await cq.message.edit_text(t(LOCALE, "del_done", label=(label or ""), chat=(chat or "")), reply_markup=admin_back_kb())
            else:
                await cq.message.edit_text(t(LOCALE, "delreq_none"), reply_markup=admin_back_kb())
            return await cq.answer()

        if data == "adm:add":
            ADMIN_STATE[uid] = {"step": "add_chat", "data": {}}
            await cq.message.edit_text(t(LOCALE, "add_prompt_chat"), reply_markup=admin_back_kb())
            return await cq.answer()

        if data == "adm:setcontent":
            ADMIN_STATE[uid] = {"step": "setcontent"}
            await cq.message.edit_text(t(LOCALE, "setcontent_prompt"), reply_markup=admin_back_kb())
            return await cq.answer()

        if data == "adm:setimg":
            ADMIN_STATE[uid] = {"step": "setimg"}
            await cq.message.edit_text(t(LOCALE, "setimg_prompt"), reply_markup=admin_back_kb())
            return await cq.answer()

        if data == "adm:back":
            ADMIN_STATE.pop(uid, None)
            await cq.message.edit_text(t(LOCALE, "admin_title") + "\\n" + t(LOCALE, "admin_desc"), reply_markup=admin_main_kb())
            return await cq.answer()

    @app.on_message(filters.private)
    async def on_admin_state_message(client: Client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        if not is_admin(uid):
            return  # ignore non-admins here

        st = ADMIN_STATE.get(uid)
        if not st:
            return  # nothing pending

        step = st.get("step")
        if step == "add_chat":
            chat = normalize_chat(message.text or "")
            if not chat:
                return await message.reply_text(t(LOCALE, "invalid"))
            st["data"]["chat"] = chat
            st["step"] = "add_url"
            return await message.reply_text(t(LOCALE, "add_prompt_url"))

        if step == "add_url":
            txt = (message.text or "").strip()
            url = "" if txt == "-" else txt
            st["data"]["url"] = url
            st["step"] = "add_label"
            return await message.reply_text(t(LOCALE, "add_prompt_label"))

        if step == "add_label":
            txt = (message.text or "").strip()
            label = "" if txt == "-" else txt
            chat = st["data"].get("chat", "")
            url = st["data"].get("url", "")
            # validation
            if chat.startswith("-100") and not url:
                ADMIN_STATE.pop(uid, None)
                return await message.reply_text(t(LOCALE, "add_need_url"))
            from handlers.user import friendly_label as f_lbl  # reuse
            ok, err = add_required(chat, url, label or f_lbl(chat))
            ADMIN_STATE.pop(uid, None)
            if not ok and err == "exists":
                return await message.reply_text(t(LOCALE, "exists", chat=chat), reply_markup=admin_main_kb())
            return await message.reply_text(t(LOCALE, "add_done", label=(label or f_lbl(chat)), chat=chat), reply_markup=admin_main_kb())

        if step == "setcontent":
            url = (message.text or "").strip()
            set_setting("CONTENT_URL", url)
            ADMIN_STATE.pop(uid, None)
            return await message.reply_text(t(LOCALE, "setcontent_ok", url=url), reply_markup=admin_main_kb())

        if step == "setimg":
            url = (message.text or "").strip()
            set_setting("START_IMAGE_URL", url)
            ADMIN_STATE.pop(uid, None)
            return await message.reply_text(t(LOCALE, "setimg_ok"), reply_markup=admin_main_kb())
