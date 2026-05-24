import os
import time
import threading
import requests
from flask import Flask
from bs4 import BeautifulSoup

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

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
        print(f"[{time.strftime('%X')}] Fetching initial cookies...")
        init_response = req_session.get(base_url, timeout=10)
        soup = BeautifulSoup(init_response.text, 'html.parser')
        payload = {"username": username, "password": password}
        for hidden in soup.find_all("input", type="hidden"):
            if hidden.get("name"):
                payload[hidden["name"]] = hidden.get("value", "")
        extra_headers = {
            "Origin": "http://new.sensix.shop:2011",
            "Referer": base_url,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        print(f"[{time.strftime('%X')}] Attempting login for '{username}'...")
        response = req_session.post(login_post_url, data=payload, headers=extra_headers, allow_redirects=True, timeout=10)
        print(f"[{time.strftime('%X')}] Response URL: {response.url}")
        print(f"[{time.strftime('%X')}] Response snippet: {response.text[:300]}")
        if "AUTHENTICATE" not in response.text and "SECURE LOGIN" not in response.text:
            print(f"[{time.strftime('%X')}] Login successful!")
            return True
        else:
            print(f"[{time.strftime('%X')}] Login failed!")
            return False
    except Exception as e:
        print(f"[{time.strftime('%X')}] Login error: {e}")
        return False

def inject_uid(url, uid, username, password, label="UID"):
    payload = {"new_uid": uid}
    try:
        response = req_session.post(url, data=payload, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        alert_div = soup.find('div', class_='alert')
        if alert_div:
            alert_text = alert_div.get_text(strip=True)
            print(f"[{time.strftime('%X')}] ALERT: {alert_text}")
        else:
            print(f"[{time.strftime('%X')}] RAW: {response.text[:300]}")
        if "AUTHENTICATE" in response.text or "SECURE LOGIN" in response.text or response.url.endswith("/login"):
            print(f"[{time.strftime('%X')}] Session expired! Relogging...")
            if auto_login(username, password):
                response = req_session.post(url, data=payload)
                soup = BeautifulSoup(response.text, 'html.parser')
                alert_div = soup.find('div', class_='alert')
                if alert_div:
                    print(f"[{time.strftime('%X')}] ALERT after relogin: {alert_div.get_text(strip=True)}")
            else:
                return False
        if alert_div:
            print(f"[{time.strftime('%X')}] {label} ({uid}) done.")
            return True
        else:
            print(f"[{time.strftime('%X')}] No alert found.")
            return False
    except Exception as e:
        print(f"[{time.strftime('%X')}] Injection error: {e}")
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
        print("Error: PANEL_USER and PANEL_PASS not set!")
        return
    main_uid = "2731370681"
    remove_uid = "27313706811"
    while not auto_login(username, password):
        print("Login failed. Retrying in 10 seconds...")
        time.sleep(10)
    print("Bot started! Injecting Main UID...")
    inject_uid(inject_url, main_uid, username, password, "Main UID")
    while True:
        try:
            time.sleep(120)
            print(f"\n[{time.strftime('%X')}] Removal cycle...")
            inject_uid(inject_url, remove_uid, username, password, "Remove UID")
            time.sleep(1)
            inject_uid(inject_url, main_uid, username, password, "Main UID")
            self_ping_logic()
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    bot_logic()
