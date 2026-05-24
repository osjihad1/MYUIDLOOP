import os
import time
import threading
import requests
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running with Auto-Relogin active!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# সেশন তৈরি করা হলো, এটি কুকি অটোমেটিক সেভ এবং আপডেট করবে
req_session = requests.Session()
req_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def auto_login(username, password):
    """
    উন্নত লগইন সিস্টেম: মূল লিঙ্ক ভিজিট করে কুকি নেওয়া এবং সিকিউরিটি হেডার পাঠানো
    """
    base_url = "http://new.sensix.shop:2011/"
    login_post_url = "http://new.sensix.shop:2011/login" 
    
    payload = {
        "username": username,
        "password": password
    }

    # সার্ভারকে বোঝানোর জন্য যে রিকোয়েস্টটি আসল ওয়েবসাইট থেকেই আসছে
    extra_headers = {
        "Origin": "http://new.sensix.shop:2011",
        "Referer": base_url
    }
    
    try:
        print(f"[{time.strftime('%X')}] 🔄 Fetching initial cookies...")
        # প্রথমে একবার ওয়েবসাইট ভিজিট করে প্রাথমিক কুকি বা টোকেন নেওয়া
        req_session.get(base_url)

        print(f"[{time.strftime('%X')}] 🔐 Attempting login for '{username}'...")
        # এবার ফর্মের ডাটা সাবমিট করা
        response = req_session.post(login_post_url, data=payload, headers=extra_headers, allow_redirects=True)
        
        # যদি লগইন পেজের "SECURE LOGIN" বা "AUTHENTICATE" লেখাগুলো রেসপন্সে আর না থাকে, তার মানে লগইন সফল!
        if "AUTHENTICATE" not in response.text and "SECURE LOGIN" not in response.text:
            print(f"[{time.strftime('%X')}] ✅ Login successful! Dashboard reached.")
            return True
        else:
            print(f"[{time.strftime('%X')}] ⚠️ Login failed! Credentials incorrect or request blocked.")
            print(f"Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[{time.strftime('%X')}] ❌ Login network error: {e}")
        return False

def inject_uid(url, uid, username, password, label="UID"):
    """
    UID ইনজেক্ট করবে। সেশন এক্সপায়ার হলে নিজে থেকে আবার লগইন করবে।
    """
    payload = {"new_uid": uid}
    try:
        response = req_session.post(url, data=payload, allow_redirects=True)
        
        # সেশন এক্সপায়ারের লজিক: রেসপন্সের ভেতর লগইন পেজের অংশ থাকলে
        if "AUTHENTICATE" in response.text or "SECURE LOGIN" in response.text or response.url.endswith("/login"):
            print(f"[{time.strftime('%X')}] 🔄 Session expired! Relogging in automatically...")
            
            if auto_login(username, password):
                response = req_session.post(url, data=payload)
            else:
                return False

        # সফলতার মেসেজ চেক করা
        if "Success: Notun UID Injected" in response.text or "Ager UID remove kora hoyeche" in response.text:
            print(f"[{time.strftime('%X')}] ✅ {label} ({uid}) successfully injected.")
            return True
        else:
            print(f"[{time.strftime('%X')}] ⚠️ Action completed but success message missing.")
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
    
    # Render ENV থেকে ইউজার এবং পাসওয়ার্ড নিচ্ছে
    username = os.environ.get("PANEL_USER")
    password = os.environ.get("PANEL_PASS")
    
    if not username or not password:
        print("❌ Error: Render Environment Variables-এ 'PANEL_USER' এবং 'PANEL_PASS' সেট করুন।")
        return

    main_uid = "2731370681"
    remove_uid = "27313706811"

    # ১. প্রথমে একবার লগইন করা
    while not auto_login(username, password):
        print("Initial login failed. Retrying in 10 seconds...")
        time.sleep(10)

    # ২. শুরুতেই মেইন ইউআইডি ইনজেক্ট
    print("🚀 Bot started! Injecting Main UID immediately...")
    inject_uid(inject_url, main_uid, username, password, "Main UID")

    # ৩. অনন্তকাল চলার লুপ
    while True:
        try:
            time.sleep(120)  # ২ মিনিট অপেক্ষা

            print("\nTriggering removal cycle...")
            inject_uid(inject_url, remove_uid, username, password, "Remove UID")

            time.sleep(1)

            inject_uid(inject_url, main_uid, username, password, "Main UID")

            # অটোমেটিক সেলফ-পিং
            self_ping_logic()

        except Exception as loop_error:
            print(f"Loop error occurred: {loop_error}")
            time.sleep(5)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    bot_logic()
