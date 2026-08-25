import json, logging, time, io, os, threading, base64, urllib.parse, hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests as http_req
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from flask import Flask

# ═══════════════════════════════════════════════════════════
#  FLASK SERVER & AUTO SELF-PING (FREE 24/7 WITHOUT UPTIMEROBOT)
# ═══════════════════════════════════════════════════════════
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running 24/7 for FREE!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

def self_ping_forever():
    """ផ្ញើសំណើដាស់ Render ស្វ័យប្រវត្តិរៀងរាល់ 8 នាទីម្តង ដើម្បីកុំឱ្យ Render Sleep"""
    time.sleep(30)
    render_url = "https://the-top-up.onrender.com"
    while True:
        try:
            http_req.get(render_url, timeout=10)
        except:
            pass
        time.sleep(480) # 8 នាទី

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
BOT_TOKEN          = "8860717390:AAE3Ai8LiP5aRXCfJfIfmowvY68ym-ySXUQ"
ADMIN_IDS          = [8807182741, 8202228991]
BOT_USERNAME       = "KhmerSmm005_bot"
ADMIN_USERNAME     = "@XGK_ganin"
GROUP_CHAT_ID      = -1003942724736

BAKONG_TOKEN       = "rbkMVUSQPooaey51jm1cD5ECnzmHyeNX7fBX4Afc16GU8k"
BANK_ACCOUNT       = "samnang_mon@bkrt"
MERCHANT_NAME      = "THE TOP UP2"
MERCHANT_CITY      = "Phnom Penh"

DEPOSIT_EXPIRE_SEC = 600
POLL_INTERVAL      = 3

executor = ThreadPoolExecutor(max_workers=30)
http_session = http_req.Session()
adapter = http_req.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50)
http_session.mount("https://", adapter)
http_session.mount("http://", adapter)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=True, num_threads=30)

USERS_FILE      = "store_users.json"
GAMES_FILE      = "store_games.json"
ORDERS_FILE     = "store_orders.json"
API_CFG_FILE    = "store_api_config.json"

def _load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return default

def _async_save(path, data):
    def _worker():
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e: logger.error(f"Save {path}: {e}")
    executor.submit(_worker)

users_db     = _load(USERS_FILE, {})
api_cfg      = _load(API_CFG_FILE, {
    "provider": "smileone",
    "api_url": "https://www.smile.one/smilecoin/api/createorder",
    "merchant_id": "",
    "api_key": ""
})

game_catalog = _load(GAMES_FILE, {
    "cat_vpn_ios": {
        "name": "🍏 VPN iOS (Apple)",
        "input_label": "Telegram Username / លេខទូរស័ព្ទ (សម្រាប់ផ្ញើ Key)",
        "packages": {
            "vpn_ios_1d":  {"name": "⚡ 1 ថ្ងៃ (Stock: 14)",  "price": 3.50,  "product_id": "vpn_ios_1d"},
            "vpn_ios_7d":  {"name": "⚡ 7 ថ្ងៃ (Stock: 23)",  "price": 7.50,  "product_id": "vpn_ios_7d"},
            "vpn_ios_30d": {"name": "⚡ 30 ថ្ងៃ (Stock: 19)", "price": 14.00, "product_id": "vpn_ios_30d"}
        }
    },
    "cat_vpn_android": {
        "name": "🤖 MeowT-Proxy Android",
        "input_label": "Telegram Username / លេខទូរស័ព្ទ (សម្រាប់ផ្ញើ Key)",
        "packages": {
            "vpn_and_1d":  {"name": "⚡ 1 ថ្ងៃ",  "price": 3.50,  "product_id": "vpn_and_1d"},
            "vpn_and_7d":  {"name": "⚡ 7 ថ្ងៃ",  "price": 7.99,  "product_id": "vpn_and_7d"},
            "vpn_and_30d": {"name": "⚡ 30 ថ្ងៃ", "price": 15.00, "product_id": "vpn_and_30d"}
        }
    },
    "game_ff": {
        "name": "🔥 Free Fire",
        "input_label": "Player ID (UID)",
        "packages": {
            "ff_vip3_combo": {"name": "👑 VIP3 (Gold+Purple+Blue Pass)", "price": 10.50, "product_id": "vip3_combo"},
            "ff_vip1_gold":  {"name": "👑 VIP1 (Monthly Pass)",          "price": 8.50,  "product_id": "vip1_gold"},
            "ff_vip1_purp":  {"name": "👑 VIP1 (Weekly Pass)",           "price": 1.89,  "product_id": "vip1_purple"},
            "ff_vip3_box":   {"name": "👑 VIP3 (Level Up / Mini Pass)",  "price": 1.55,  "product_id": "vip3_box"},
            "ff_115":        {"name": "💎 115 Diamonds",                  "price": 0.99,  "product_id": "115"},
            "ff_240":        {"name": "💎 240 Diamonds",                  "price": 1.99,  "product_id": "240"},
            "ff_610":        {"name": "💎 610 Diamonds",                  "price": 4.80,  "product_id": "610"},
            "ff_1240":       {"name": "💎 1,240 Diamonds",                "price": 9.50,  "product_id": "1240"}
        }
    },
    "game_roblox": {
        "name": "🟥 Roblox (Robux)",
        "input_label": "Roblox Username",
        "packages": {
            "rbx_80":    {"name": "🪙 80 Robux",     "price": 1.00,   "product_id": "rbx_80"},
            "rbx_160":   {"name": "🪙 160 Robux",    "price": 2.00,   "product_id": "rbx_160"},
            "rbx_240":   {"name": "🪙 240 Robux",    "price": 3.00,   "product_id": "rbx_240"},
            "rbx_400":   {"name": "🪙 400 Robux",    "price": 4.85,   "product_id": "rbx_400"},
            "rbx_800":   {"name": "🪙 800 Robux",    "price": 9.00,   "product_id": "rbx_800"},
            "rbx_1700":  {"name": "🪙 1,700 Robux",  "price": 18.00,  "product_id": "rbx_1700"},
            "rbx_4500":  {"name": "🪙 4,500 Robux",  "price": 45.90,  "product_id": "rbx_4500"},
            "rbx_10000": {"name": "🪙 10,000 Robux", "price": 75.00,  "product_id": "rbx_10000"},
            "rbx_22500": {"name": "🪙 22,500 Robux", "price": 150.00, "product_id": "rbx_22500"}
        }
    }
})

game_orders  = _load(ORDERS_FILE, {})
waiting      = {}

def is_admin(uid): return int(uid) in ADMIN_IDS

def _notify_admins(msg, reply_markup=None):
    for aid in ADMIN_IDS:
        executor.submit(lambda a=aid: _safe_send_admin(a, msg, reply_markup))

def _safe_send_admin(aid, msg, reply_markup=None):
    try: bot.send_message(aid, msg, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e: logger.warning(f"Admin send error to {aid}: {e}")

def _safe_send_group(msg):
    try: bot.send_message(GROUP_CHAT_ID, msg, parse_mode="HTML")
    except Exception as e: logger.warning(f"Group send error: {e}")

def _track_user_and_alert(message):
    uid = message.chat.id
    uid_str = str(uid)
    u = message.from_user
    name = (u.first_name or "") + (" " + u.last_name if u.last_name else "")
    name = name.strip() or "អតិថិជន"
    username = f"@{u.username}" if u.username else "គ្មាន Username"
    is_new_user = uid_str not in users_db

    users_db[uid_str] = {
        "name": name,
        "username": u.username or "",
        "last": int(time.time()),
        "first_join": users_db.get(uid_str, {}).get("first_join", int(time.time())),
        "banned": users_db.get(uid_str, {}).get("banned", False)
    }
    _async_save(USERS_FILE, users_db)

    if is_new_user and not is_admin(uid):
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        join_alert = (
            f"🔔 <b>មានសមាជិកថ្មីទើបតែចុចចូល Bot!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>ឈ្មោះ:</b> {name} ({username})\n"
            f"🆔 <b>Telegram ID:</b> <code>{uid}</code>\n"
            f"⏰ <b>ពេលវេលា:</b> <code>{time_str}</code>\n"
            f"👥 <b>សរុបអ្នកប្រើប្រាស់:</b> <b>{len(users_db)}</b> នាក់"
        )
        _notify_admins(join_alert)
        executor.submit(lambda: _safe_send_group(join_alert))

def is_banned(uid): return bool(users_db.get(str(uid), {}).get("banned", False))

def _execute_real_topup(player_id, product_id):
    url = api_cfg.get("api_url", "").strip()
    m_id = api_cfg.get("merchant_id", "").strip()
    key = api_cfg.get("api_key", "").strip()
    provider = api_cfg.get("provider", "smileone")

    if not url or not key: return False, "មិនទាន់កំណត់ API Key"
    try:
        if provider == "smileone":
            sign_str = f"uid={m_id}&product_id={product_id}&userid={player_id}&key={key}"
            sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
            payload = {"uid": m_id, "userid": player_id, "product_id": product_id, "sign": sign}
            r = http_session.post(url, data=payload, timeout=12)
            res = r.json()
            if res.get("status") == 200: return True, str(res.get("order_id", "SUCCESS"))
            return False, res.get("message", "API Error")
        else:
            payload = {"merchant_id": m_id, "api_key": key, "player_id": player_id, "product_id": product_id}
            r = http_session.post(url, json=payload, timeout=12)
            res = r.json()
            if res.get("status") in [200, "success", "SUCCESS", 1]: return True, str(res.get("order_id", res.get("id", "SUCCESS")))
            return False, res.get("message", res.get("error", "API Error"))
    except Exception as e: return False, str(e)

def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.row("🛍️ ហាងទំនិញ & សេវាកម្ម (Shop)")
    kb.row("📋 ប្រវត្តិបញ្ជាទិញ", "💬 ទំនាក់ទំនង Admin")
    return kb

def admin_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.row("👥 ឆែកមើលអតិថិជន (Users)", "📊 ស្ថិតិទូទៅ")
    kb.row("📋 បញ្ជី Orders ទាំងអស់", "📦 គ្រប់គ្រងមុខទំនិញ")
    kb.row("➕ បន្ថែមប្រភេទ", "➕ បន្ថែមកញ្ចប់ទំនិញ")
    kb.row("⚙️ កំណត់ API", "🔌 ឆែកមើល API")
    kb.row("📢 ផ្សព្វផ្សាយដំណឹង", "🏠 ផ្ទាំងដើមភ្ញៀវ")
    return kb

def cancel_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("✕ បោះបង់ (Cancel)")
    return kb

def games_menu_kb(prefix="user_game"):
    btns, row = [], []
    for gid, ginfo in game_catalog.items():
        row.append(InlineKeyboardButton(f"{ginfo['name']}", callback_data=f"{prefix}:{gid}"))
        if len(row) == 2: btns.append(row); row = []
    if row: btns.append(row)
    return InlineKeyboardMarkup(btns)

def game_packages_kb(gid, is_admin_panel=False):
    ginfo = game_catalog.get(gid, {})
    pkgs = ginfo.get("packages", {})
    btns = []
    for pid, pinfo in pkgs.items():
        if is_admin_panel:
            btns.append([InlineKeyboardButton(f"🗑️ លុប: {pinfo['name']} • ${pinfo['price']:.2f}", callback_data=f"adm_del_pkg:{gid}:{pid}")])
        else:
            btns.append([InlineKeyboardButton(f"✨ {pinfo['name']} ➔ 💵 ${pinfo['price']:.2f}", callback_data=f"user_buy_pkg:{gid}:{pid}")])
    if is_admin_panel:
        btns.append([InlineKeyboardButton(f"🗑️ លុបប្រភេទទាំងមូល ({ginfo.get('name','')})", callback_data=f"adm_del_entire_cat:{gid}")])
    btns.append([InlineKeyboardButton("🔙 ថយក្រោយ (Back)", callback_data="back_games")])
    return InlineKeyboardMarkup(btns)

def _create_khqr_card_image(qr_str, merchant_name, amount):
    try:
        r = http_session.post(
            "https://api.bakongrelay.com/v1/generate_khqr_image",
            json={"qr": qr_str},
            headers={"Authorization": f"Bearer {BAKONG_TOKEN}", "Content-Type": "application/json"},
            timeout=5,
        )
        if r.ok and r.json().get("responseCode") == 0:
            img_b64 = r.json().get("data", {}).get("image", "")
            if img_b64:
                if "," in img_b64: img_b64 = img_b64.split(",", 1)[1]
                buf = io.BytesIO(base64.b64decode(img_b64))
                buf.name = "khqr.png"
                buf.seek(0)
                return buf
    except: pass

    try:
        encoded_data = urllib.parse.quote(qr_str)
        cloud_url = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={encoded_data}&format=png&margin=10"
        res = http_session.get(cloud_url, timeout=5)
        if res.ok and len(res.content) > 100:
            buf = io.BytesIO(res.content)
            buf.name = "qr.png"
            buf.seek(0)
            return buf
    except: pass
    return None

def _check_bakong(md5):
    try:
        r = http_session.post(
            "https://api.bakongrelay.com/v1/check_payment",
            json={"md5": str(md5)},
            headers={"Authorization": f"Bearer {BAKONG_TOKEN}", "Content-Type": "application/json"},
            timeout=4
        )
        if r.ok:
            data = r.json()
            if data.get("responseCode") == 0 and (data.get("data", {}).get("status") == "PAID" or data.get("status") == "PAID"):
                return True
    except: pass
    return False

def _process_paid_order(oid):
    order = game_orders.get(oid)
    if not order: return

    uid = int(order["uid"])
    player_id = order["player_id"]
    pkg_name = order["pkg_name"]
    game_name = order["game_name"]
    buyer_info = users_db.get(str(uid), {})
    buyer_name = buyer_info.get("name", "ភ្ញៀវ")
    buyer_username = f"@{buyer_info['username']}" if buyer_info.get("username") else "គ្មាន Username"

    order["status"] = "paid_waiting_admin_approval"
    _async_save(ORDERS_FILE, game_orders)

    bot.send_message(uid,
        f"✅ <b>ការទូទាត់ប្រាក់ទទួលបានជោគជ័យ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Order ID: <code>{oid}</code>\n"
        f"📦 សេវាកម្ម: <b>{game_name}</b> ({pkg_name})\n"
        f"⏳ <b>ប្រព័ន្ធបានជូនដំណឹងទៅ Admin រួចហើយ កំពុងរង់ចាំ Admin ចុចបញ្ជាក់ការទិញ!</b>\n"
        f"📞 ទំនាក់ទំនង Admin: {ADMIN_USERNAME}",
        parse_mode="HTML", reply_markup=main_kb())

    admin_confirm_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ បញ្ជាក់ (Approve)", callback_data=f"adm_appr:{oid}"),
            InlineKeyboardButton("❌ បោះបង់ (Reject)", callback_data=f"adm_rej:{oid}")
        ]
    ])

    admin_alert_msg = (
        f"💰 <b>ភ្ញៀវបានស្កេនបង់លុយជោគជ័យ (PAID)!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Order ID:</b> <code>{oid}</code>\n"
        f"👤 <b>អ្នកទិញ:</b> {buyer_name} (<code>{uid}</code>)\n"
        f"📦 <b>សេវា:</b> <b>{game_name}</b>\n"
        f"⚡ <b>កញ្ចប់:</b> <b>{pkg_name}</b>\n"
        f"💰 <b>តម្លៃ:</b> <b>${order['price']:.2f}</b>\n"
        f"🎯 <b>Target / UID:</b> <code>{player_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👉 <b>សូមចុច «បញ្ជាក់» ដើម្បីអនុម័តឱ្យភ្ញៀវ ឬ «បោះបង់»:</b>"
    )
    _notify_admins(admin_alert_msg, admin_confirm_kb)

def _watch_order_payment(oid, md5_hash, sent_msg_id, uid, amount, pkg_name, player_id, game_name):
    start_time = time.time()
    expire_time = start_time + DEPOSIT_EXPIRE_SEC

    while time.time() < expire_time:
        order = game_orders.get(oid)
        if not order or order.get("status") not in ("pending_payment",): return

        if _check_bakong(md5_hash):
            try: bot.delete_message(uid, sent_msg_id)
            except: pass
            _process_paid_order(oid)
            return
        time.sleep(POLL_INTERVAL)

    order = game_orders.get(oid)
    if order and order.get("status") == "pending_payment":
        order["status"] = "expired"
        _async_save(ORDERS_FILE, game_orders)
        try: bot.edit_message_caption(chat_id=uid, message_id=sent_msg_id, caption="⏰ <b>QR Code ផុតកំណត់ហើយ! សូមធ្វើការកុម្ម៉ង់ម្តងទៀត។</b>", parse_mode="HTML")
        except: pass

def _send_order_qr(uid, player_id, pkg, game_name):
    amount = float(pkg["price"])
    pkg_name = pkg["name"]
    prod_id = pkg.get("product_id", "")
    oid = f"ORD{int(time.time())%1000000:06d}"
    buyer_info = users_db.get(str(uid), {})
    buyer_name = buyer_info.get("name", "ភ្ញៀវ")
    buyer_username = f"@{buyer_info['username']}" if buyer_info.get("username") else "គ្មាន Username"

    try:
        from bakong_khqr import KHQR
        k = KHQR(BAKONG_TOKEN)
        qr_str = k.create_qr(
            bank_account=BANK_ACCOUNT, merchant_name=MERCHANT_NAME,
            merchant_city=MERCHANT_CITY, amount=round(amount, 2),
            currency="USD", bill_number=f"{oid}"[:25], static=False
        )
        md5_hash = k.generate_md5(qr_str)
    except:
        qr_str = f"https://khqr.bakong?amount={amount}&acc={BANK_ACCOUNT}"
        md5_hash = hashlib.md5(qr_str.encode()).hexdigest()

    game_orders[oid] = {
        "uid": str(uid),
        "game_name": game_name,
        "player_id": player_id,
        "pkg_name": pkg_name,
        "product_id": prod_id,
        "price": amount,
        "status": "pending_payment",
        "md5": md5_hash,
        "ts": int(time.time())
    }
    _async_save(ORDERS_FILE, game_orders)

    admin_confirm_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ បញ្ជាក់ (Approve)", callback_data=f"adm_appr:{oid}"),
            InlineKeyboardButton("❌ បោះបង់ (Reject)", callback_data=f"adm_rej:{oid}")
        ]
    ])

    admin_direct_msg = (
        f"🛒 <b>មានភ្ញៀវកុម្ម៉ង់ទិញទំនិញថ្មី!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Order ID:</b> <code>{oid}</code>\n"
        f"👤 <b>អ្នកទិញ:</b> {buyer_name} ({buyer_username}) | <code>{uid}</code>\n"
        f"📦 <b>សេវា/ហ្គេម:</b> <b>{game_name}</b>\n"
        f"⚡ <b>កញ្ចប់:</b> <b>{pkg_name}</b>\n"
        f"💰 <b>តម្លៃ:</b> <b>${amount:.2f}</b>\n"
        f"🎯 <b>Target / UID:</b> <code>{player_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👉 <b>Admin អាចចុច «បញ្ជាក់» ដើម្បីអនុម័តជូនភ្ញៀវភ្លាមៗ ឬចុច «បោះបង់»:</b>"
    )
    _notify_admins(admin_direct_msg, admin_confirm_kb)

    group_pending_msg = (
        f"🛒 <b>មានការកុម្ម៉ង់ទំនិញថ្មី!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Order ID:</b> <code>{oid}</code>\n"
        f"👤 <b>អ្នកទិញ:</b> {buyer_name} ({buyer_username})\n"
        f"📦 <b>សេវា:</b> <b>{game_name}</b>\n"
        f"⚡ <b>កញ្ចប់:</b> <b>{pkg_name}</b>\n"
        f"💰 <b>តម្លៃ:</b> <b>${amount:.2f}</b>\n"
        f"🎯 <b>Target/UID:</b> <code>{player_id}</code>"
    )
    executor.submit(lambda: _safe_send_group(group_pending_msg))

    cap = (
        f"💸 <b>ស្កេនទូទាត់ប្រាក់ (KHQR)</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📦 សេវា: <b>{game_name}</b>\n"
        f"👤 គណនី: <code>{player_id}</code>\n"
        f"⚡ កញ្ចប់: <b>{pkg_name}</b>\n"
        f"💰 តម្លៃត្រូវបង់: <b>${amount:.2f}</b>\n"
        f"⏳ <b>រយៈពេល 10 នាទី</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📱 Scan តាម ABA, Wing, Bakong..."
    )
    user_check_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ខ្ញុំបានបង់ប្រាក់រួចហើយ (Check)", callback_data=f"chk_order:{oid}")]])

    img_buf = _create_khqr_card_image(qr_str, MERCHANT_NAME, amount)
    sent_msg = None
    if img_buf:
        try: sent_msg = bot.send_photo(uid, img_buf, caption=cap, parse_mode="HTML", reply_markup=user_check_btn)
        except: pass
    if not sent_msg:
        sent_msg = bot.send_message(uid, cap + f"\n\n<code>{qr_str}</code>", parse_mode="HTML", reply_markup=user_check_btn)

    executor.submit(_watch_order_payment, oid, md5_hash, sent_msg.message_id, uid, amount, pkg_name, player_id, game_name)

@bot.message_handler(commands=["start", "admin"])
def cmd_start(message):
    uid = message.chat.id
    waiting.pop(uid, None)
    _track_user_and_alert(message)
    if is_banned(uid): return

    if is_admin(uid) and message.text == "/admin":
        bot.send_message(uid,
            f"👑 <b>Admin Dashboard — Multi-Admin Mode</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👥 Admin IDs: <code>{ADMIN_IDS}</code>\n"
            f"👥 អតិថិជនសរុប: <b>{len(users_db)}</b> នាក់\n"
            f"📦 ប្រភេទសេវាសរុប: <b>{len(game_catalog)}</b>\n"
            f"📋 ការបញ្ជាទិញសរុប: <b>{len(game_orders)}</b>\n"
            f"👥 Group Chat ID: <code>{GROUP_CHAT_ID}</code>",
            parse_mode="HTML", reply_markup=admin_kb())
        return

    kb = admin_kb() if is_admin(uid) else main_kb()
    welcome_text = (
        f"🔥 <b>ស្វាគមន៍មកកាន់ហាង Game Top-Up & VPN Proxy Store!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🍏 <b>VPN iOS (Apple)</b> & 🤖 <b>MeowT-Proxy Android</b>\n"
        f"🔥 <b>Free Fire (VIP Pass)</b> & 🟥 <b>Roblox (Robux)</b>\n"
        f"👉 ជ្រើសរើសកញ្ចប់ 👉 ស្កេនទូទាត់ KHQR ដំណើរការភ្លាមៗ!\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👉 សូមចុច <b>🛍️ ហាងទំនិញ & សេវាកម្ម (Shop)</b> ដើម្បីចាប់ផ្តើម៖"
    )
    bot.send_message(uid, welcome_text, parse_mode="HTML", reply_markup=kb)

@bot.message_handler(content_types=["text", "photo"])
def handle_msg(message):
    uid = message.chat.id
    uid_str = str(uid)
    text = (message.text or message.caption or "").strip()
    step = waiting.get(uid)
    _track_user_and_alert(message)

    if is_banned(uid) and not is_admin(uid): return

    if text in ("✕ Cancel", "❌ Cancel", "✕ បោះបង់ (Cancel)", "🏠 ផ្ទាំងដើមភ្ញៀវ", "🏠 Menu ភ្ញៀវ"):
        waiting.pop(uid, None)
        kb = admin_kb() if is_admin(uid) else main_kb()
        bot.send_message(uid, "🏠 Menu ដើម", reply_markup=kb)
        return

    # ADMIN
    if is_admin(uid):
        if "ឆែកមើលអតិថិជន" in text or "Users" in text:
            users_sorted = sorted(users_db.items(), key=lambda x: x[1].get("last", 0), reverse=True)
            if not users_sorted:
                bot.send_message(uid, "❌ មិនទាន់មានអតិថិជនណាម្នាក់នៅឡើយទេ!", reply_markup=admin_kb())
                return

            lines = [f"👥 <b>បញ្ជីអតិថិជនទាំងអស់ ({len(users_sorted)} នាក់):</b>\n━━━━━━━━━━━━━━━━━━"]
            for idx, (u_id, u_info) in enumerate(users_sorted[:30], 1):
                name = u_info.get("name", "ភ្ញៀវ")
                uname = f"@{u_info['username']}" if u_info.get("username") else "គ្មាន Username"
                last_active = datetime.fromtimestamp(u_info.get("last", time.time())).strftime("%Y-%m-%d %H:%M")
                status = "🚫 Banned" if u_info.get("banned", False) else "🟢 សកម្ម"
                lines.append(f"<b>{idx}. {name}</b> ({uname})\n🆔 <code>{u_id}</code> | {status}\n⏰ សកម្មចុងក្រោយ: <code>{last_active}</code>\n─────────────────")
            bot.send_message(uid, "\n".join(lines)[:4000], parse_mode="HTML", reply_markup=admin_kb())
            return

        if "ស្ថិតិទូទៅ" in text:
            total_orders = len(game_orders)
            completed_orders = sum(1 for o in game_orders.values() if o.get("status") == "✅ completed")
            total_revenue = sum(float(o.get("price", 0)) for o in game_orders.values() if o.get("status") == "✅ completed")
            total_users = len(users_db)
            bot.send_message(uid,
                f"📊 <b>ស្ថិតិទូទៅនៃហាង</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👥 ចំនួនអតិថិជនសរុប: <b>{total_users} នាក់</b>\n"
                f"📦 ការបញ្ជាទិញសរុប: <b>{total_orders}</b>\n"
                f"✅ ការបញ្ជាទិញជោគជ័យ: <b>{completed_orders}</b>\n"
                f"💰 ចំណូលសរុប (Completed): <b>${total_revenue:.2f}</b>\n"
                f"🛍️ ប្រភេទសេវាកម្មសកម្ម: <b>{len(game_catalog)}</b>",
                parse_mode="HTML", reply_markup=admin_kb())
            return

        if "កំណត់ API" in text:
            waiting[uid] = "set_api_url"
            bot.send_message(uid, "⚙️ <b>ជំហានទី ១: សូមផ្ញើ API Order URL:</b>", parse_mode="HTML", reply_markup=cancel_kb())
            return

        if step == "set_api_url":
            api_cfg["api_url"] = text.strip()
            waiting[uid] = "set_api_uid"
            bot.send_message(uid, "🆔 <b>ជំហានទី ២: សូមផ្ញើ Merchant UID / Customer ID:</b>", parse_mode="HTML", reply_markup=cancel_kb())
            return

        if step == "set_api_uid":
            api_cfg["merchant_id"] = text.strip()
            waiting[uid] = "set_api_key"
            bot.send_message(uid, "🔑 <b>ជំហានទី ៣: សូមផ្ញើ API Secret Key:</b>", parse_mode="HTML", reply_markup=cancel_kb())
            return

        if step == "set_api_key":
            api_cfg["api_key"] = text.strip()
            _async_save(API_CFG_FILE, api_cfg)
            waiting.pop(uid, None)
            bot.send_message(uid, "✅ <b>បានរក្សាទុក Game Top-Up API ជោគជ័យ!</b>", parse_mode="HTML", reply_markup=admin_kb())
            return

        if "ឆែកមើល API" in text:
            bot.send_message(uid, f"🌐 URL: <code>{api_cfg.get('api_url')}</code>\n🆔 Merchant ID: <code>{api_cfg.get('merchant_id')}</code>", parse_mode="HTML", reply_markup=admin_kb())
            return

        if "បន្ថែមប្រភេទ" in text:
            waiting[uid] = "adm_add_game_name"
            bot.send_message(uid, "📦 <b>សូមផ្ញើឈ្មោះសេវាកម្ម/ហ្គេមថ្មី:</b>", parse_mode="HTML", reply_markup=cancel_kb())
            return

        if step == "adm_add_game_name":
            gid = f"cat_{int(time.time())}"
            game_catalog[gid] = {"name": text, "input_label": "Player ID / Username", "packages": {}}
            _async_save(GAMES_FILE, game_catalog)
            waiting.pop(uid, None)
            bot.send_message(uid, f"✅ បានបន្ថែម «{text}» ជោគជ័យ!", parse_mode="HTML", reply_markup=admin_kb())
            return

        if "បន្ថែមកញ្ចប់ទំនិញ" in text:
            bot.send_message(uid, "📦 <b>សូមជ្រើសរើសប្រភេទដែលចង់បន្ថែមកញ្ចប់:</b>", parse_mode="HTML", reply_markup=games_menu_kb(prefix="adm_sel_game_add_pkg"))
            return

        if isinstance(step, dict) and step.get("step") == "adm_input_pkg_name":
            gid = step["gid"]
            waiting[uid] = {"step": "adm_input_pkg_price", "gid": gid, "name": text}
            bot.send_message(uid, f"💰 <b>សូមផ្ញើតម្លៃជាដុល្លារ ($) សម្រាប់ «{text}»:</b>", parse_mode="HTML", reply_markup=cancel_kb())
            return

        if isinstance(step, dict) and step.get("step") == "adm_input_pkg_price":
            try:
                price = float(text.replace("$", "").strip())
                waiting[uid] = {"step": "adm_input_pkg_pid", "gid": step["gid"], "name": step["name"], "price": price}
                bot.send_message(uid, "🆔 <b>សូមផ្ញើ Product ID នៃ API (Code):</b>", parse_mode="HTML", reply_markup=cancel_kb())
            except: bot.send_message(uid, "❌ សូមបញ្ចូលតម្លៃជាលេខ $ ត្រឹមត្រូវ!")
            return

        if isinstance(step, dict) and step.get("step") == "adm_input_pkg_pid":
            gid = step["gid"]
            pid = f"pkg_{int(time.time())}"
            game_catalog[gid]["packages"][pid] = {"name": step["name"], "price": step["price"], "product_id": text.strip()}
            _async_save(GAMES_FILE, game_catalog)
            waiting.pop(uid, None)
            bot.send_message(uid, f"✅ បានបន្ថែមកញ្ចប់ <b>{step['name']} (${step['price']:.2f})</b> ជោគជ័យ!", parse_mode="HTML", reply_markup=admin_kb())
            return

        if "គ្រប់គ្រងមុខទំនិញ" in text:
            bot.send_message(uid, "📦 <b>សូមជ្រើសរើសប្រភេទដើម្បីមើល/លុបកញ្ចប់:</b>", parse_mode="HTML", reply_markup=games_menu_kb(prefix="adm_manage_game"))
            return

        if "បញ្ជី Orders" in text:
            if not game_orders:
                bot.send_message(uid, "❌ មិនទាន់មានការបញ្ជាទិញទេ!", reply_markup=admin_kb()); return
            lines = ["<b>📋 បញ្ជី Orders (15 ចុងក្រោយ)</b>\n━━━━━━━━━━━━━━━━━━"]
            for oid, o in list(game_orders.items())[-15:]:
                lines.append(f"🆔 <code>{oid}</code> | 📦 {o.get('game_name','?')}\n👤 User: <code>{o.get('player_id','?')}</code> | {o.get('pkg_name','?')} (${o.get('price',0):.2f})\n🚦 Status: <b>{o.get('status','?')}</b>\n─────────────────")
            bot.send_message(uid, "\n".join(lines)[:4000], parse_mode="HTML", reply_markup=admin_kb())
            return

        if "ផ្សព្វផ្សាយ" in text:
            waiting[uid] = "broadcast_msg"
            bot.send_message(uid, "📢 <b>ផ្ញើសារ (Text/Photo) ដែលត្រូវផ្សព្វផ្សាយ:</b>", parse_mode="HTML", reply_markup=cancel_kb())
            return

        if step == "broadcast_msg":
            waiting.pop(uid, None)
            def _broadcast():
                for u_id in list(users_db.keys()):
                    try:
                        if message.photo: bot.send_photo(int(u_id), message.photo[-1].file_id, caption=message.caption or "", parse_mode="HTML")
                        else: bot.send_message(int(u_id), message.text, parse_mode="HTML")
                    except: pass
            executor.submit(_broadcast)
            bot.send_message(uid, "✅ កំពុងដំណើរការផ្សព្វផ្សាយសារក្នុងល្បឿនលឿន!", reply_markup=admin_kb())
            return

    # USER
    if "ហាងទំនិញ" in text or "Shop" in text:
        bot.send_message(uid, "🛍️ <b>សូមជ្រើសរើសសេវាកម្មដែលលោកអ្នកចង់ទិញ៖</b>", parse_mode="HTML", reply_markup=games_menu_kb(prefix="user_game"))
        return

    if isinstance(step, dict) and step.get("step") == "input_game_target_for_qr":
        target_id = text.strip()
        gid = step["gid"]
        pid = step["pid"]
        ginfo = game_catalog.get(gid, {})
        pkg = ginfo.get("packages", {}).get(pid)

        if not pkg:
            waiting.pop(uid, None)
            bot.send_message(uid, "❌ កញ្ចប់នេះរកមិនឃើញទេ!", reply_markup=main_kb()); return

        waiting.pop(uid, None)
        _send_order_qr(uid, target_id, pkg, ginfo.get("name", "Service"))
        return

    if "ប្រវត្តិ" in text or "History" in text:
        my_orders = {oid: o for oid, o in game_orders.items() if o.get("uid") == uid_str}
        if not my_orders:
            bot.send_message(uid, "📋 <b>ប្រវត្តិការទិញ</b>\n\n❌ គ្មានទិន្នន័យបញ្ជាទិញទេ!", parse_mode="HTML", reply_markup=main_kb())
            return
        lines = ["📋 <b>ប្រវត្តិបញ្ជាទិញរបស់អ្នក</b>\n━━━━━━━━━━━━━━━━━━"]
        for oid, o in sorted(my_orders.items(), key=lambda x: x[1].get("ts", 0), reverse=True)[:10]:
            lines.append(f"🆔 <code>{oid}</code> | 📦 {o.get('game_name','?')}\n👤 Target: <code>{o.get('player_id','?')}</code>\n⚡ {o.get('pkg_name','?')} | <b>${o.get('price',0):.2f}</b>\n🚦 Status: <b>{o.get('status','pending')}</b>\n─────────────────")
        bot.send_message(uid, "\n".join(lines), parse_mode="HTML", reply_markup=main_kb())
        return

    if "Support" in text or "ទំនាក់ទំនង" in text:
        bot.send_message(uid, f"💬 <b>ផ្នែកបម្រើអតិថិជន (Support)</b>\n━━━━━━━━━━━━━━━━━━\n📞 Admin: {ADMIN_USERNAME}", parse_mode="HTML", reply_markup=main_kb())
        return

    bot.send_message(uid, "❓ សូមប្រើប្រាស់ Menu ខាងក្រោម៖", reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(call):
    uid = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data.startswith("adm_appr:"):
        if not is_admin(uid): return
        oid = data.split(":")[1]
        order = game_orders.get(oid)
        if not order: bot.send_message(uid, "❌ មិនមានទិន្នន័យ Order នេះទេ!"); return
        if order.get("status") == "✅ completed": bot.send_message(uid, f"⚠️ Order <code>{oid}</code> ត្រូវបានបញ្ជាក់រួចរាល់ហើយ!", parse_mode="HTML"); return

        target_uid = int(order["uid"])
        player_id = order["player_id"]
        prod_id = order["product_id"]
        pkg_name = order["pkg_name"]
        game_name = order["game_name"]

        success, api_res = _execute_real_topup(player_id, prod_id)
        order["status"] = "✅ completed"
        order["api_order_id"] = api_res if success else "APPROVED_BY_ADMIN"
        _async_save(ORDERS_FILE, game_orders)

        try:
            bot.edit_message_text(
                f"✅ <b>Order <code>{oid}</code> ត្រូវបានបញ្ជាក់ (Approved) ដោយជោគជ័យ!</b>\n"
                f"📦 {game_name} ({pkg_name}) សម្រាប់ <code>{player_id}</code>",
                chat_id=uid, message_id=call.message.message_id, parse_mode="HTML"
            )
        except: pass

        bot.send_message(target_uid,
            f"🎉 <b>ការបញ្ជាទិញរបស់អ្នកត្រូវបាន Admin បញ្ជាក់ជោគជ័យ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 វិក្កយបត្រ: <code>{oid}</code>\n"
            f"📦 មុខទំនិញ: <b>{game_name}</b>\n"
            f"⚡ កញ្ចប់: <b>{pkg_name}</b>\n"
            f"👤 គណនី: <code>{player_id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✨ ទំនិញ/Item/Key ត្រូវបានបញ្ចូល/ផ្ញើជូនរួចរាល់ហើយ សូមអរគុណ!",
            parse_mode="HTML", reply_markup=main_kb())

        group_appr_msg = (
            f"✅ <b>ការបញ្ជាទិញត្រូវបានបញ្ជាក់ (Approved)!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Order ID:</b> <code>{oid}</code>\n"
            f"📦 <b>សេវា/ហ្គេម:</b> <b>{game_name}</b> ({pkg_name})\n"
            f"🎯 <b>Target:</b> <code>{player_id}</code>\n"
            f"💰 <b>តម្លៃ:</b> <b>${order['price']:.2f}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>ស្ថានភាព: បញ្ចប់ជោគជ័យ ១០០%</b>"
        )
        executor.submit(lambda: _safe_send_group(group_appr_msg))
        return

    if data.startswith("adm_rej:"):
        if not is_admin(uid): return
        oid = data.split(":")[1]
        order = game_orders.get(oid)
        if not order: return

        order["status"] = "❌ cancelled_by_admin"
        _async_save(ORDERS_FILE, game_orders)

        try:
            bot.edit_message_text(f"❌ <b>Order <code>{oid}</code> ត្រូវបានបោះបង់ (Rejected) ដោយ Admin!</b>", chat_id=uid, message_id=call.message.message_id, parse_mode="HTML")
        except: pass

        target_uid = int(order["uid"])
        bot.send_message(target_uid,
            f"⚠️ <b>ការបញ្ជាទិញ <code>{oid}</code> ត្រូវបានបដិសេធ/បោះបង់ដោយ Admin!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📦 សេវា: <b>{order['game_name']}</b> ({order['pkg_name']})\n"
            f"📞 សូមទាក់ទងមកកាន់ Admin ({ADMIN_USERNAME}) ដើម្បីដោះស្រាយ ឬសងប្រាក់ត្រឡប់វិញ។",
            parse_mode="HTML", reply_markup=main_kb())

        group_rej_msg = (
            f"❌ <b>ការបញ្ជាទិញត្រូវបានបោះបង់ (Rejected)!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Order ID:</b> <code>{oid}</code>\n"
            f"📦 <b>សេវា/ហ្គេម:</b> <b>{order['game_name']}</b>\n"
            f"🎯 <b>Target:</b> <code>{order['player_id']}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <b>ស្ថានភាព: បោះបង់ដោយ Admin</b>"
        )
        executor.submit(lambda: _safe_send_group(group_rej_msg))
        return

    if data.startswith("user_game:"):
        gid = data.split(":")[1]
        ginfo = game_catalog.get(gid)
        if not ginfo: return
        try: bot.edit_message_text(f"🛍️ <b>{ginfo['name']}</b>\nសូមជ្រើសរើសកញ្ចប់ទំនិញ/រយៈពេលដែលអ្នកត្រូវការ:", chat_id=uid, message_id=call.message.message_id, parse_mode="HTML", reply_markup=game_packages_kb(gid, is_admin_panel=False))
        except: pass
        return

    if data.startswith("user_buy_pkg:"):
        _, gid, pid = data.split(":")
        ginfo = game_catalog.get(gid, {})
        pkg = ginfo.get("packages", {}).get(pid)
        if not pkg: return

        input_label = ginfo.get("input_label", "Player ID / Telegram Username")
        waiting[uid] = {"step": "input_game_target_for_qr", "gid": gid, "pid": pid}
        bot.send_message(uid,
            f"📦 <b>សេវាកម្ម:</b> {ginfo.get('name')}\n"
            f"⚡ <b>កញ្ចប់ជ្រើសរើស:</b> {pkg['name']}\n"
            f"💰 <b>តម្លៃ:</b> ${pkg['price']:.2f}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✍️ <b>សូមផ្ញើ {input_label} របស់អ្នកមកទីនេះ:</b>",
            parse_mode="HTML", reply_markup=cancel_kb())
        return

    if data.startswith("adm_sel_game_add_pkg:"):
        if not is_admin(uid): return
        gid = data.split(":")[1]
        waiting[uid] = {"step": "adm_input_pkg_name", "gid": gid}
        bot.send_message(uid, f"📦 <b>បន្ថែមកញ្ចប់សម្រាប់ «{game_catalog[gid]['name']}»</b>\n\n✍️ សូមផ្ញើឈ្មោះកញ្ចប់ថ្មី:", parse_mode="HTML", reply_markup=cancel_kb())
        return

    if data.startswith("adm_manage_game:"):
        if not is_admin(uid): return
        gid = data.split(":")[1]
        try: bot.edit_message_text(f"📦 <b>បញ្ជីកញ្ចប់ក្នុង {game_catalog[gid]['name']} (ចុចដើម្បីលុប):</b>", chat_id=uid, message_id=call.message.message_id, parse_mode="HTML", reply_markup=game_packages_kb(gid, is_admin_panel=True))
        except: pass
        return

    if data.startswith("adm_del_pkg:"):
        if not is_admin(uid): return
        _, gid, pid = data.split(":")
        if gid in game_catalog and pid in game_catalog[gid].get("packages", {}):
            del game_catalog[gid]["packages"][pid]
            _async_save(GAMES_FILE, game_catalog)
            bot.send_message(uid, "✅ បានលុបកញ្ចប់នេះរួចរាល់!", reply_markup=admin_kb())
        return

    if data.startswith("adm_del_entire_cat:"):
        if not is_admin(uid): return
        gid = data.split(":")[1]
        if gid in game_catalog:
            deleted_name = game_catalog[gid].get("name", "")
            del game_catalog[gid]
            _async_save(GAMES_FILE, game_catalog)
            bot.send_message(uid, f"✅ បានលុបប្រភេទសេវាកម្ម «{deleted_name}» ទាំងមូលរួចរាល់!", reply_markup=admin_kb())
        return

    if data == "back_games":
        try: bot.edit_message_text("🛍️ <b>សូមជ្រើសរើសសេវាកម្មដែលលោកអ្នកចង់ទិញ៖</b>", chat_id=uid, message_id=call.message.message_id, parse_mode="HTML", reply_markup=games_menu_kb(prefix="user_game"))
        except: pass
        return

    if data.startswith("chk_order:"):
        oid = data.split(":")[1]
        order = game_orders.get(oid)
        if not order: bot.send_message(uid, "❌ មិនមានវិក្កយបត្រនេះទេ!"); return
        if _check_bakong(order.get("md5", "")): _process_paid_order(oid)
        else: bot.send_message(uid, "⏳ <b>មិនទាន់ឃើញប្រតិបត្តិការបង់ប្រាក់នៅឡើយទេ!</b>", parse_mode="HTML")
        return

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=self_ping_forever, daemon=True).start()
    logger.info("⚡ Self-Ping 24/7 Multi-Admin Store Bot is running...")
    bot.infinity_polling(timeout=20, long_polling_timeout=15)
