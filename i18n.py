
TEXT = {
    "id": {
        "start_caption": "Join grup/channel berikut agar konten terbuka:",
        "btn_join": "Join {label}",
        "btn_check": "Check ✅",
        "thanks_content": "✅ Terima kasih! Berikut link konten:\n{content_url}",
        "missing_header": "❌ Kamu belum join ke grup/channel berikut:",
        "missing_footer": "Silakan klik tombol Join, lalu tekan 'Check ✅' lagi.",

        # Admin UI
        "admin_only": "Khusus admin.",
        "admin_title": "🔧 Panel Admin",
        "admin_desc": "Kelola daftar wajib join & pengaturan.",
        "btn_list": "📋 Daftar Wajib Join",
        "btn_add": "➕ Tambah Wajib Join",
        "btn_del": "🗑 Hapus Wajib Join",
        "btn_setcontent": "🔗 Set CONTENT_URL",
        "btn_setimg": "🖼 Set START_IMAGE_URL",
        "btn_back": "⬅️ Kembali",

        "list_empty": "Daftar kosong. Tambahkan dengan tombol ➕.",
        "list_header": "Daftar wajib join:",
        "del_pick": "Pilih item yang akan dihapus:",
        "del_done": "Dihapus: {label} ({chat})",
        "add_prompt_chat": "Kirim @username / -100id / t.me/slug untuk ditambahkan:",
        "add_prompt_url": "Kirim URL undangan (opsional, balas pesan ini atau kirim '-' untuk lewati):",
        "add_prompt_label": "Kirim label tampilan (opsional, balas pesan ini atau kirim '-' untuk lewati):",
        "add_need_url": "Untuk -100..., sertakan URL undangan t.me (invite link).",
        "add_done": "Ditambahkan: {label} ({chat})",
        "exists": "Sudah ada: {chat}",

        "setcontent_prompt": "Kirim URL konten baru:",
        "setcontent_ok": "CONTENT_URL di-set: {url}",
        "setimg_prompt": "Kirim URL gambar baru:",
        "setimg_ok": "START_IMAGE_URL di-set.",

        "invalid": "Input tidak valid.",
    },
    "en": {
        "start_caption": "Join the following group(s)/channel(s) to unlock the content:",
        "btn_join": "Join {label}",
        "btn_check": "Check ✅",
        "thanks_content": "✅ Thanks! Here is the content link:\n{content_url}",
        "missing_header": "❌ You haven't joined these group(s)/channel(s):",
        "missing_footer": "Please tap Join, then press 'Check ✅' again.",

        "admin_only": "Admins only.",
        "admin_title": "🔧 Admin Panel",
        "admin_desc": "Manage required joins & settings.",
        "btn_list": "📋 View Required",
        "btn_add": "➕ Add Required",
        "btn_del": "🗑 Remove Required",
        "btn_setcontent": "🔗 Set CONTENT_URL",
        "btn_setimg": "🖼 Set START_IMAGE_URL",
        "btn_back": "⬅️ Back",

        "list_empty": "List is empty. Use ➕ to add.",
        "list_header": "Required to join:",
        "del_pick": "Choose an item to remove:",
        "del_done": "Deleted: {label} ({chat})",
        "add_prompt_chat": "Send @username / -100id / t.me/slug to add:",
        "add_prompt_url": "Send invite URL (optional, reply this message or send '-' to skip):",
        "add_prompt_label": "Send display label (optional, reply or '-' to skip):",
        "add_need_url": "For -100... please include an invite link (t.me/+...).",
        "add_done": "Added: {label} ({chat})",
        "exists": "Already exists: {chat}",

        "setcontent_prompt": "Send new content URL:",
        "setcontent_ok": "CONTENT_URL set: {url}",
        "setimg_prompt": "Send new image URL:",
        "setimg_ok": "START_IMAGE_URL updated.",

        "invalid": "Invalid input.",
    }
}

def t(lang, key, **kwargs):
    lang = (lang or 'id').lower()
    d = TEXT.get(lang, TEXT["id"])
    s = d.get(key, TEXT["id"].get(key, key))
    return s.format(**kwargs)
