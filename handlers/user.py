# handlers/user.py
from __future__ import annotations

import logging
from urllib.parse import urlparse
from typing import Optional

from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, WebpageCurlFailed
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.enums import ChatMemberStatus  # << penting: enum status

from db import get_all_required, get_setting
from config import DEFAULT_CONTENT_URL, DEFAULT_START_IMAGE_URL, LOCALE, BUTTONS_PER_ROW
from i18n import t

log = logging.getLogger(__name__)


# ---------- UI helpers ----------
def friendly_label(chat: str) -> str:
    chat = (chat or "").strip()
    if chat.startswith("@"):
        return chat[1:]
    if chat.startswith("-100"):
        return f"Channel {chat[-4:]}"
    return chat or "Channel"


def _sanitize_join_url(chat: str, url: Optional[str]) -> Optional[str]:
    """
    Kembalikan URL join yang valid:
      - url ada → rapikan (https://t.me/…)
      - url kosong + chat publik (@username) → https://t.me/username
      - privat (-100…) tanpa url → None
    """
    chat = (chat or "").strip()
    url = (url or "").strip().strip('"\'')

    if url:
        if url.startswith("t.me/") or url.startswith("telegram.me/"):
            url = "https://" + url
        if url.startswith("http://t.me/"):
            url = url.replace("http://", "https://", 1)
        if url.startswith("http://telegram.me/"):
            url = url.replace("http://", "https://", 1)
        u = urlparse(url)
        if u.scheme in ("http", "https") and u.netloc:
            return url
        return None

    if chat.startswith("@"):
        return f"https://t.me/{chat[1:]}"
    return None


def build_join_kb(reqs, locale: str) -> InlineKeyboardMarkup:
    rows, row = [], []
    for it in reqs:
        label = (getattr(it, "label", None) or friendly_label(getattr(it, "chat", ""))).strip()
        chat = getattr(it, "chat", "") or ""
        url = getattr(it, "url", "") or ""

        join_url = _sanitize_join_url(chat, url)
        if not join_url:
            log.warning("Skip invalid join url for chat=%r url=%r", chat, url)
            continue

        row.append(InlineKeyboardButton(t(locale, "btn_join", label=label), url=join_url))
        if len(row) >= BUTTONS_PER_ROW:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(t(locale, "btn_check"), callback_data="check_membership")])
    return InlineKeyboardMarkup(rows)


# ---------- membership helpers ----------
def _username_from_url(url: str) -> Optional[str]:
    try:
        u = urlparse(url or "")
        if u.netloc in ("t.me", "telegram.me"):
            path = (u.path or "").strip("/")
            if path:
                slug = path.split("/")[0]
                if slug and not slug.startswith("+"):  # jangan pakai joinchat/+hash
                    return slug
    except Exception:
        pass
    return None


async def _resolve_ident(client: Client, chat: str | int, url_hint: Optional[str] = None) -> int:
    """
    Terima '@username' atau '-100…' atau int. Selalu resolve via get_chat()
    supaya entity ter-cache. Jika -100… gagal, coba derive dari url_hint (t.me/slug).
    """
    # 1) @username
    if isinstance(chat, str) and chat.strip().startswith("@"):
        c = await client.get_chat(chat.strip())
        return c.id

    # 2) "-100…"/angka string
    if isinstance(chat, str) and chat.strip().lstrip("-").isdigit():
        ident = int(chat.strip())
        try:
            c = await client.get_chat(ident)
            return c.id
        except Exception as e:
            log.warning("get_chat(int) gagal untuk %r: %s", ident, e)
            slug = _username_from_url(url_hint or "")
            if slug:
                c = await client.get_chat(f"@{slug}")
                return c.id
            raise

    # 3) sudah int
    if isinstance(chat, int):
        c = await client.get_chat(chat)
        return c.id

    # 4) fallback: coba direct
    c = await client.get_chat(str(chat))
    return c.id


def _status_is_ok(status) -> bool:
    """
    Samakan antara enum ChatMemberStatus.* dan string 'member'/'administrator'/'creator'/'owner'
    """
    # enum?
    if isinstance(status, ChatMemberStatus):
        ok_set = {
            getattr(ChatMemberStatus, "MEMBER", None),
            getattr(ChatMemberStatus, "ADMINISTRATOR", None),
            # pyrogram v2 umumnya pakai OWNER, beberapa bot lama pakai CREATOR
            getattr(ChatMemberStatus, "OWNER", None),
            getattr(ChatMemberStatus, "CREATOR", None),
        }
        return status in ok_set

    # string / lainnya
    val = str(status).lower()
    return val in {"member", "administrator", "creator", "owner"}


async def is_member(client: Client, chat: str | int, user_id: int, url_hint: Optional[str] = None) -> bool:
    try:
        ident = await _resolve_ident(client, chat, url_hint=url_hint)
        m = await client.get_chat_member(ident, user_id)
        return _status_is_ok(m.status)
    except UserNotParticipant:
        return False
    except Exception as e:
        log.warning("is_member error for chat=%r user=%r: %s", chat, user_id, e)
        return False


# ---------- register handlers ----------
def register(app: Client):

    @app.on_message(filters.command("start") & filters.private)
    async def on_start(client: Client, message: Message):
        reqs = get_all_required()
        caption = t(LOCALE, "start_caption")
        img_src = get_setting("START_IMAGE_URL", DEFAULT_START_IMAGE_URL) or DEFAULT_START_IMAGE_URL
        kb = build_join_kb(reqs, LOCALE)

        try:
            await message.reply_photo(img_src, caption=caption, reply_markup=kb)
        except WebpageCurlFailed:
            try:
                await message.reply_photo("assets/hero.jpg", caption=caption, reply_markup=kb)
            except Exception:
                await message.reply_text(caption, reply_markup=kb)
        except Exception:
            await message.reply_text(caption, reply_markup=kb)

    @app.on_callback_query(filters.regex("^check_membership$"))
    async def on_check(client: Client, cq: CallbackQuery):
        reqs = get_all_required()
        user_id = cq.from_user.id

        missing = []
        for it in reqs:
            chat = getattr(it, "chat", "") or ""
            url = getattr(it, "url", "") or ""
            if not await is_member(client, chat, user_id, url_hint=url):
                missing.append(it)

        if missing:
            rows, row = [], []
            for it in missing:
                label = (getattr(it, "label", None) or friendly_label(getattr(it, "chat", ""))).strip()
                chat = getattr(it, "chat", "") or ""
                url = getattr(it, "url", "") or ""
                join_url = _sanitize_join_url(chat, url)
                if join_url:
                    row.append(InlineKeyboardButton(t(LOCALE, "btn_join", label=label), url=join_url))
                    if len(row) >= BUTTONS_PER_ROW:
                        rows.append(row); row = []
            if row:
                rows.append(row)
            rows.append([InlineKeyboardButton(t(LOCALE, "btn_check"), callback_data="check_membership")])

            lines = [t(LOCALE, "missing_header")]
            for it in missing:
                ch = getattr(it, "chat", "") or ""
                lines.append(f"• {(getattr(it, 'label', None) or friendly_label(ch))} ({ch})")
            lines += ["", t(LOCALE, "missing_footer")]

            await cq.message.reply_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))
        else:
            content = get_setting("CONTENT_URL", DEFAULT_CONTENT_URL) or DEFAULT_CONTENT_URL
            await cq.message.reply_text(t(LOCALE, "thanks_content", content_url=content), disable_web_page_preview=False)

        await cq.answer()

    # ---- diagnostic: /checkme ----
    @app.on_message(filters.command("checkme") & filters.private)
    async def check_me(client: Client, message: Message):
        reqs = get_all_required()
        uid = message.from_user.id
        lines, ok_all = ["Diag:"], True
        for it in reqs:
            ch = getattr(it, "chat", "") or ""
            url = getattr(it, "url", "") or ""
            try:
                ident = await _resolve_ident(client, ch, url_hint=url)
                m = await client.get_chat_member(ident, uid)
                lines.append(f"- {ch} → {m.status}")
                if not _status_is_ok(m.status):
                    ok_all = False
            except Exception as e:
                ok_all = False
                lines.append(f"- {ch} → ERROR {type(e).__name__}")
        lines.append(f"\nRESULT: {'OK' if ok_all else 'MISSING'}")
        await message.reply_text("\n".join(lines))
