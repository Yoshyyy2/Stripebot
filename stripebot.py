import telebot
from telebot import types
import requests
import re
import json
import os
import time
import threading
import random
import string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── CONFIG ───────────────────────────────────────────────
BOT_TOKEN  = '8603869007:AAGO09lmBqufzrE2TrkATvr8FMrRVKCirPg'
ADMIN_ID   = 6601184733          # your Telegram user ID
API_KEY    = 'afuona_2026'
API_URL    = 'http://localhost:8000'  # change to your hosted API URL
# ──────────────────────────────────────────────────────────

bot = telebot.TeleBot(BOT_TOKEN, num_threads=10)

USERS_FILE   = 'stripe_users.json'
MAX_MASS     = 10
COOLDOWN_CHK = 5
COOLDOWN_MSS = 15

# ─── USER MANAGEMENT ──────────────────────────────────────
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE) as f:
                d = json.load(f)
                return set(d.get('approved', [])), d.get('pending', {})
        except:
            pass
    return set(), {}

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump({'approved': list(approved_users), 'pending': pending_requests}, f, indent=2)

approved_users, pending_requests = load_users()

def is_approved(uid):
    return uid == ADMIN_ID or uid in approved_users

# ─── COOLDOWN ─────────────────────────────────────────────
user_cooldowns = {}

def check_cooldown(chat_id, kind):
    now = time.time()
    limit = COOLDOWN_CHK if kind == 'chk' else COOLDOWN_MSS
    last = user_cooldowns.get(f"{chat_id}_{kind}", 0)
    diff = now - last
    if diff < limit:
        return False, int(limit - diff) + 1
    user_cooldowns[f"{chat_id}_{kind}"] = now
    return True, 0

# ─── PROXY STORE ──────────────────────────────────────────
user_proxies = {}   # chat_id -> proxy string

def get_proxy(chat_id):
    return user_proxies.get(chat_id) or user_proxies.get('global')

# ─── DEFAULT SITES ────────────────────────────────────────
DEFAULT_SITES = [
    "store.segway.com",
    "www.asedeals.com",
    "www.miamihitches.com",
    "universal-akb.com",
]
_site_idx = 0
_site_lock = threading.Lock()

def next_site():
    global _site_idx
    with _site_lock:
        s = DEFAULT_SITES[_site_idx % len(DEFAULT_SITES)]
        _site_idx += 1
        return s

user_custom_sites = {}

def get_site(chat_id):
    return user_custom_sites.get(chat_id, next_site())

# ─── API HELPERS ──────────────────────────────────────────
def api_check(card, site, proxy):
    """Call /process endpoint"""
    try:
        r = requests.get(
            f"{API_URL}/process",
            params={
                'key':   API_KEY,
                'site':  site,
                'cc':    card,
                'proxy': proxy,
            },
            timeout=60,
            verify=False
        )
        if r.status_code == 200:
            return r.json()
        return {'Response': f'API Error {r.status_code}', 'Status': 'Error'}
    except Exception as e:
        return {'Response': str(e)[:80], 'Status': 'Error'}

def api_test_proxy(proxy):
    try:
        r = requests.get(
            f"{API_URL}/test_proxy",
            params={'proxy': proxy},
            timeout=15,
            verify=False
        )
        return r.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}

def api_test_site(site, proxy):
    try:
        r = requests.get(
            f"{API_URL}/test_site",
            params={'key': API_KEY, 'site': site, 'proxy': proxy},
            timeout=60,
            verify=False
        )
        return r.json()
    except Exception as e:
        return {'working': False, 'response': str(e)}

# ─── SEND HELPERS ─────────────────────────────────────────
def send_safe(chat_id, text, **kw):
    try:
        return bot.send_message(chat_id, text, **kw)
    except:
        return None

def edit_safe(chat_id, msg_id, text, **kw):
    try:
        return bot.edit_message_text(text, chat_id, msg_id, **kw)
    except:
        return None

# ─── STATUS FORMATTER ─────────────────────────────────────
def fmt_status(status, response):
    s = status.lower()
    resp_low = response.lower()
    if s == 'approved' or 'card added' in resp_low:
        return '✅', 'Approved'
    elif 'insufficient' in resp_low or 'funds' in resp_low:
        return '💰', 'Insufficient Funds'
    elif '3d' in resp_low or 'authentication' in resp_low or 'secure' in resp_low:
        return '🔐', '3D Secure'
    elif 'cvv' in resp_low or 'cvc' in resp_low or 'security code' in resp_low:
        return '⚠️', 'CVV Mismatch'
    else:
        return '❌', 'Declined'

def fmt_result(card, result, username='User'):
    status  = result.get('Status', 'Unknown')
    response = result.get('Response', 'Unknown')
    icon, label = fmt_status(status, response)

    text  = "╔══════════════════════════╗\n"
    text += "║  💳 STRIPE CHECK RESULT  ║\n"
    text += "╚══════════════════════════╝\n\n"
    text += f"<b>Card:</b> <code>{card}</code>\n\n"
    text += f"<b>Status:</b> {icon} {label}\n"
    text += f"<b>Response:</b> {response}\n\n"
    text += f"<b>Gateway:</b> Stripe\n"
    text += f"<b>Checked by:</b> @{username}\n"
    text += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return text

# ─── REQUIRE APPROVAL ─────────────────────────────────────
def require_approval(fn):
    def wrapper(msg):
        if not is_approved(msg.from_user.id):
            send_safe(msg.chat.id,
                "╔══════════════════╗\n"
                "║  🚫 ACCESS DENIED ║\n"
                "╚══════════════════╝\n\n"
                "You need admin approval.\n"
                "Use /request to apply.")
            return
        return fn(msg)
    return wrapper

# ══════════════════════════════════════════════════════════
#  COMMANDS
# ══════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def cmd_start(msg):
    uid = msg.from_user.id
    if not is_approved(uid):
        send_safe(msg.chat.id,
            "╔════════════════════════╗\n"
            "║   💳 STRIPE CHECKER   ║\n"
            "╚════════════════════════╝\n\n"
            "🔒 Access required.\n"
            "📝 Use /request to get access.")
        return

    text  = "╔════════════════════════╗\n"
    text += "║   💳 STRIPE CHECKER   ║\n"
    text += "╚════════════════════════╝\n\n"
    text += "🎯 <b>COMMANDS</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💳 /schk - Single card check\n"
    text += "📦 /smass - Mass card check\n"
    text += "🌐 /ssite - Set custom site\n"
    text += "🗑️ /rsite - Remove custom site\n"
    text += "📍 /mysite - Current site\n"
    text += "🔌 /sproxy - Set your proxy\n"
    text += "🧪 /tsite - Test a site\n"
    text += "❓ /help - Help\n"

    if uid == ADMIN_ID:
        text += "\n⚙️ <b>ADMIN</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "🌐 /gproxy - Set global proxy\n"
        text += "👥 /users - List users\n"
        text += "⏳ /pending - Pending requests\n"
        text += "📢 /broadcast - Broadcast\n"

    text += "\n✨ Powered by Stripe API"
    send_safe(msg.chat.id, text, parse_mode='HTML')


@bot.message_handler(commands=['help'])
@require_approval
def cmd_help(msg):
    text  = "📚 <b>HOW TO USE</b>\n\n"
    text += "<b>/schk</b> card|mm|yy|cvv\n"
    text += "  Single card check\n\n"
    text += "<b>/smass</b>\ncard1|mm|yy|cvv\ncard2|mm|yy|cvv\n"
    text += "  Mass check (max 10)\n\n"
    text += "<b>/sproxy</b> host:port:user:pass\n"
    text += "  Set your proxy (required!)\n\n"
    text += "<b>/ssite</b> https://example.com\n"
    text += "  Set custom Stripe site\n\n"
    text += "<b>/tsite</b> example.com\n"
    text += "  Test if site has Stripe\n\n"
    text += "⚠️ Proxy is required for checking!"
    send_safe(msg.chat.id, text, parse_mode='HTML')


@bot.message_handler(commands=['request'])
def cmd_request(msg):
    uid = msg.from_user.id
    if is_approved(uid):
        send_safe(msg.chat.id, "✅ You already have access!")
        return
    if uid in pending_requests:
        send_safe(msg.chat.id, "⏳ Your request is already pending...")
        return

    uname = msg.from_user.username or 'No username'
    fname = msg.from_user.first_name or 'Unknown'

    pending_requests[uid] = {
        'username': uname,
        'name': fname,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_users()

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
        types.InlineKeyboardButton("❌ Deny",    callback_data=f"deny_{uid}")
    )
    send_safe(ADMIN_ID,
        f"📥 <b>Access Request</b>\n\n"
        f"👤 {fname}\n🔗 @{uname}\n🆔 {uid}\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='HTML', reply_markup=markup)
    send_safe(msg.chat.id, "📤 Request sent! Waiting for admin approval...")


@bot.callback_query_handler(func=lambda c: c.data.startswith(('approve_', 'deny_')))
def cb_approval(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!")
        return
    action, uid = call.data.split('_', 1)
    uid = int(uid)
    if action == 'approve':
        approved_users.add(uid)
        pending_requests.pop(uid, None)
        save_users()
        bot.answer_callback_query(call.id, "✅ Approved!")
        edit_safe(call.message.chat.id, call.message.message_id, f"✅ User {uid} approved!")
        send_safe(uid, "🎉 <b>Approved!</b>\n\nYou now have access.\nType /start to begin.", parse_mode='HTML')
    else:
        pending_requests.pop(uid, None)
        save_users()
        bot.answer_callback_query(call.id, "❌ Denied!")
        edit_safe(call.message.chat.id, call.message.message_id, f"❌ User {uid} denied!")
        send_safe(uid, "🚫 Your access request was denied.")


# ─── PROXY COMMANDS ───────────────────────────────────────
@bot.message_handler(commands=['sproxy'])
@require_approval
def cmd_set_proxy(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        send_safe(msg.chat.id, "Usage: /sproxy host:port:user:pass")
        return
    proxy = parts[1].strip()
    status = send_safe(msg.chat.id, "⏳ Testing proxy...")
    result = api_test_proxy(proxy)
    if result.get('success'):
        user_proxies[msg.chat.id] = proxy
        txt = f"✅ Proxy working!\n🌐 IP: {result.get('ip', 'Unknown')}"
    else:
        txt = f"❌ Proxy failed: {result.get('error', 'Unknown error')}"
    if status:
        edit_safe(msg.chat.id, status.message_id, txt)
    else:
        send_safe(msg.chat.id, txt)


@bot.message_handler(commands=['gproxy'])
def cmd_global_proxy(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        send_safe(msg.chat.id, "Usage: /gproxy host:port:user:pass")
        return
    proxy = parts[1].strip()
    status = send_safe(msg.chat.id, "⏳ Testing global proxy...")
    result = api_test_proxy(proxy)
    if result.get('success'):
        user_proxies['global'] = proxy
        txt = f"✅ Global proxy set!\n🌐 IP: {result.get('ip', 'Unknown')}"
    else:
        txt = f"❌ Proxy failed: {result.get('error', 'Unknown error')}"
    if status:
        edit_safe(msg.chat.id, status.message_id, txt)
    else:
        send_safe(msg.chat.id, txt)


# ─── SITE COMMANDS ────────────────────────────────────────
@bot.message_handler(commands=['ssite'])
@require_approval
def cmd_set_site(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        send_safe(msg.chat.id, "Usage: /ssite https://example.com")
        return
    site = parts[1].strip().replace('https://', '').replace('http://', '').split('/')[0]
    user_custom_sites[msg.chat.id] = site
    send_safe(msg.chat.id, f"✅ Custom site set: {site}")


@bot.message_handler(commands=['rsite'])
@require_approval
def cmd_remove_site(msg):
    if msg.chat.id in user_custom_sites:
        del user_custom_sites[msg.chat.id]
        send_safe(msg.chat.id, "✅ Custom site removed. Using default rotation.")
    else:
        send_safe(msg.chat.id, "ℹ️ No custom site set.")


@bot.message_handler(commands=['mysite'])
@require_approval
def cmd_my_site(msg):
    custom = user_custom_sites.get(msg.chat.id)
    if custom:
        send_safe(msg.chat.id, f"🔧 Custom site: {custom}")
    else:
        send_safe(msg.chat.id, f"📌 Using rotation:\n" + "\n".join(f"• {s}" for s in DEFAULT_SITES))


@bot.message_handler(commands=['tsite'])
@require_approval
def cmd_test_site(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        send_safe(msg.chat.id, "Usage: /tsite example.com")
        return
    site = parts[1].strip().replace('https://', '').replace('http://', '').split('/')[0]
    proxy = get_proxy(msg.chat.id)
    if not proxy:
        send_safe(msg.chat.id, "❌ Set a proxy first with /sproxy")
        return
    status = send_safe(msg.chat.id, f"🧪 Testing site: {site}...")
    result = api_test_site(site, proxy)
    working = result.get('working', False)
    txt  = f"🌐 <b>Site Test: {site}</b>\n\n"
    txt += f"{'✅ Working' if working else '❌ Not Working'}\n"
    txt += f"Status: {result.get('status', 'Unknown')}\n"
    txt += f"Response: {result.get('response', 'Unknown')}"
    if status:
        edit_safe(msg.chat.id, status.message_id, txt, parse_mode='HTML')
    else:
        send_safe(msg.chat.id, txt, parse_mode='HTML')


# ─── SINGLE CHECK ─────────────────────────────────────────
@bot.message_handler(commands=['schk'])
@require_approval
def cmd_schk(msg):
    ok, wait = check_cooldown(msg.chat.id, 'chk')
    if not ok:
        send_safe(msg.chat.id, f"⏳ Cooldown: wait {wait}s")
        return

    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        send_safe(msg.chat.id, "Usage: /schk card|mm|yy|cvv")
        return

    card = parts[1].strip()
    if not re.match(r'^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$', card):
        send_safe(msg.chat.id, "❌ Invalid format. Use: number|mm|yy|cvv")
        return

    proxy = get_proxy(msg.chat.id)
    if not proxy:
        send_safe(msg.chat.id,
            "❌ No proxy set!\n\n"
            "Set one with:\n/sproxy host:port:user:pass")
        return

    site = get_site(msg.chat.id)
    status = send_safe(msg.chat.id, f"⏳ Checking card...\n💳 {card}\n🌐 {site}")
    if not status:
        return

    result = api_check(card, site, proxy)
    uname = msg.from_user.username or 'User'
    edit_safe(msg.chat.id, status.message_id, fmt_result(card, result, uname), parse_mode='HTML')


# ─── MASS CHECK ───────────────────────────────────────────
@bot.message_handler(commands=['smass'])
@require_approval
def cmd_smass(msg):
    ok, wait = check_cooldown(msg.chat.id, 'mass')
    if not ok:
        send_safe(msg.chat.id, f"⏳ Cooldown: wait {wait}s")
        return

    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        send_safe(msg.chat.id, f"Usage: /smass card1|mm|yy|cvv\ncard2|mm|yy|cvv\n\nMax: {MAX_MASS}")
        return

    cards = [c.strip() for c in parts[1].strip().split('\n') if c.strip()]
    if not cards:
        send_safe(msg.chat.id, "❌ No cards found.")
        return
    if len(cards) > MAX_MASS:
        send_safe(msg.chat.id, f"❌ Max {MAX_MASS} cards at once.")
        return

    proxy = get_proxy(msg.chat.id)
    if not proxy:
        send_safe(msg.chat.id,
            "❌ No proxy set!\n\nSet one with:\n/sproxy host:port:user:pass")
        return

    site = get_site(msg.chat.id)
    status = send_safe(msg.chat.id, f"⏳ Checking {len(cards)} cards...")
    if not status:
        return

    results = []
    with ThreadPoolExecutor(max_workers=min(5, len(cards))) as ex:
        futures = {ex.submit(api_check, card, site, proxy): card for card in cards}
        for i, future in enumerate(as_completed(futures), 1):
            card = futures[future]
            try:
                res = future.result()
            except Exception as e:
                res = {'Response': str(e)[:50], 'Status': 'Error'}
            results.append((card, res))
            edit_safe(msg.chat.id, status.message_id, f"⏳ Checked {i}/{len(cards)}...")

    # Count results
    approved = sum(1 for _, r in results if r.get('Status') == 'Approved')
    declined = len(results) - approved

    text  = "╔══════════════════════════╗\n"
    text += "║  📦 MASS CHECK RESULTS  ║\n"
    text += "╚══════════════════════════╝\n\n"
    text += f"✅ Approved: {approved} | ❌ Declined: {declined}\n"
    text += f"📊 Total: {len(results)}\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for card, res in results:
        status_txt = res.get('Status', 'Unknown')
        response   = res.get('Response', 'Unknown')
        icon, _    = fmt_status(status_txt, response)
        text += f"{icon} <code>{card}</code>\n"
        text += f"└ {response}\n\n"

    text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"👤 By: @{msg.from_user.username or 'User'}"

    edit_safe(msg.chat.id, status.message_id, text, parse_mode='HTML')


# ─── ADMIN COMMANDS ───────────────────────────────────────
@bot.message_handler(commands=['users'])
def cmd_users(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    if not approved_users:
        send_safe(msg.chat.id, "📭 No approved users.")
        return
    text = "👥 <b>Approved Users:</b>\n\n"
    for i, uid in enumerate(approved_users, 1):
        text += f"{i}. 🆔 {uid}\n"
    send_safe(msg.chat.id, text, parse_mode='HTML')


@bot.message_handler(commands=['pending'])
def cmd_pending(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    if not pending_requests:
        send_safe(msg.chat.id, "📭 No pending requests.")
        return
    text = "⏳ <b>Pending Requests:</b>\n\n"
    for uid, info in pending_requests.items():
        text += f"👤 {info['name']}\n🔗 @{info['username']}\n🆔 {uid}\n\n"
    send_safe(msg.chat.id, text, parse_mode='HTML')


@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        send_safe(msg.chat.id, "Usage: /broadcast Your message")
        return
    btext = parts[1].strip()
    ok = fail = 0
    for uid in approved_users:
        try:
            send_safe(uid, f"📢 <b>BROADCAST</b>\n\n{btext}", parse_mode='HTML')
            ok += 1
        except:
            fail += 1
        time.sleep(0.3)
    send_safe(msg.chat.id, f"✅ Sent: {ok}\n❌ Failed: {fail}")


# ─── MAIN ─────────────────────────────────────────────────
if __name__ == '__main__':
    print("🚀 Stripe Bot started!")
    print(f"📡 API: {API_URL}")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Bot crashed: {e}, restarting in 5s...")
            time.sleep(5)
