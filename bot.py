import os
import time
import threading
import requests
from flask import Flask
from bs4 import BeautifulSoup

app = Flask('')

@app.route('/')
def home():
    return "Bot is running with Auto-Relogin active!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

req_session = requests.Session()
req_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def auto_login(username, password):
    base_url = "http://new.sensix.shop:2011/"
    login_post_url = "http://new.sensix.shop:2011/login"

    try:
        print(f"[{time.strftime('%X')}] 🔄 Fetching initial cookies...")
        init_response = req_session.get(base_url, timeout=10)

        soup = BeautifulSoup(init_response.text, 'html.parser')
        payload = {"username": username, "password": password}

        for hidden in soup.find_all("input", type="hidden"):
            if hidden.get("name"):
                payload[hidden["name"]] = hidden.get("value", "")

        print(f"[{time.strftime('%X')}] Payload keys: {list(payload.keys())}")

        extra_headers = {
            "Origin": "http://new.sensix.shop:2011",
            "Referer": base_url,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        print(f"[{time.strftime('%X')}] 🔐 Attempting login for '{username}'...")
        response = req_session.post(
            login_post_url,
            data=payload,
            headers=extra_headers,
            allow_redirects=True,
            timeout=10
        )

        print(f"[{time.strftime('%X')}] Login response URL: {response.url}")
        print(f"[{time.strftime('%X')}] Response snippet: {response.text[:300]}")

        if "AUTHENTICATE" not in response.text and "SECURE LOGIN" not in response.text:
            print(f"[{time.strftime('%X')}] ✅ Login successful! Dashboard reached.")
            return True
        else:
            print(f"[{time.strftime('%X')}] ⚠️ Login failed!")
            return False

    except Exception as e:
        print(f"[{time.strftime('%X')}] ❌ Login error: {e}")
        return False


def inject_uid(url, uid, username, password, label="UID"):
    payload = {"new_uid": uid}
    try:
        response = req_session.post(url, data=payload, allow_redirects=True)

        # Alert message বের করা
        soup = BeautifulSoup(response.text, 'html.parser')
        alert_div = soup.find('div', class_='alert')
        if alert_div:
            alert_text = alert_div.get_text(strip=True)
            print(f"[{time.strftime('%X')}] [ALERT MSG]: {alert_text}")
        else:
            print(f"[{time.strftime('%X')}] [RAW snippet]: {response.text[:300]}")

        # Session expired চেক
        if "AUTHENTICATE" in response.text or "SECURE LOGIN" in response.text or response.url.endswith("/login"):
            print(f"[{time.strftime('%X')}] 🔄 Session expired! Relogging in automatically...")
            if auto_login(username, password):
                response = req_session.post(url, data=payload)
                soup = BeautifulSoup(response.text, 'html.parser')
                alert_div = soup.find('div', class_='alert')
                if alert_div:
                    print(f"[{time.strftime('%X')}] [ALERT after relogin]: {alert_div.get_text(strip=True)}")
            else:
                return False

        # Success চেক — alert text দেখার পর এটা আপডেট করা হবে
        if alert_div and alert_div.get_text(strip=True):
            print(f"[{time.strftime('%X')}] ✅ {label} ({uid}) injection done.")
            return True
        else:
            print(f"[{time.strftime('%X')}] ⚠️ No alert message found.")
            return False

    except Exception as e:
        print(f"[{time.strftime('%X')}] ❌ Error during injection: {e}")
        return False


def self_ping_logic():
    self_url = os.environ.get("RENDER_EXTERNAL_URL")
    if self_url:
        try:
            requests.get(self_url)
        except:
            pass


def bot_logic():
    inject_url = "http://new.sensix.shop:2011/user_update_uid"

    username = os.environ.get("PANEL_USER")
    password = os.environ.get("PANEL_PASS")

    if not username or not password:
        print("❌ Error: 'PANEL_USER' এবং 'PANEL_PASS' Render Environment Variables-এ সেট করুন।")
        return

    main_uid = "2731370681"
    remove_uid = "27313706811"

    # প্রথমে লগইন
    while not auto_login(username, password):
        print("Initial login failed. Retrying in 10 seconds...")
        time.sleep(10)

    # শুরুতেই main UID inject
    print("🚀 Bot started! Injecting Main UID immediately...")
    inject_uid(inject_url, main_uid, username, password, "Main UID")

    # মেইন লুপ
    while True:
        try:
            time.sleep(120)

            print(f"\n[{time.strftime('%X')}] Triggering removal cycle...")
            inject_uid(inject_url, remove_uid, username, password, "Remove UID")

            time.sleep(1)

            inject_uid(inject_url, main_uid, username, password, "Main UID")

            self_ping_logic()

        except Exception as loop_error:
            print(f"Loop error: {loop_error}")
            time.sleep(5)


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    bot_logic()def auto_login(username, password):
    base_url = "http://new.sensix.shop:2011/"
    login_post_url = "http://new.sensix.shop:2011/login"
    
    try:
        # প্রথমে GET করে response থেকে hidden field/token খোঁজা
        init_response = req_session.get(base_url, timeout=10)
        
        # HTML থেকে hidden input field বের করা (যদি থাকে)
        # যেমন: _token, csrf_token ইত্যাদি
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(init_response.text, 'html.parser')
        
        payload = {"username": username, "password": password}
        
        # সব hidden field যোগ করা
        for hidden in soup.find_all("input", type="hidden"):
            if hidden.get("name"):
                payload[hidden["name"]] = hidden.get("value", "")
        
        print(f"Payload keys: {list(payload.keys())}")  # debug
        
        extra_headers = {
            "Origin": "http://new.sensix.shop:2011",
            "Referer": base_url,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = req_session.post(
            login_post_url, 
            data=payload, 
            headers=extra_headers, 
            allow_redirects=True,
            timeout=10
        )
        
        print(f"Login response URL: {response.url}")  # debug
        print(f"Response snippet: {response.text[:300]}")  # debug
        
        if "AUTHENTICATE" not in response.text and "SECURE LOGIN" not in response.text:
            print(f"✅ Login successful!")
            return True
        else:
            print(f"⚠️ Login failed!")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
