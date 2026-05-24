import os
import time
import threading
import requests
from flask import Flask

# Flask server create kora hocche self-ping er jonno
app = Flask('')

@app.route('/')
def home():
    return "Bot is running and alive!"

def run_web_server():
    # Defaut port 8080 te server colbe
    app.run(host='0.0.0.0', port=8080)

def inject_uid(url, headers, uid, label="UID"):
    payload = {"new_uid": uid}
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code in [200, 302]:
            print(f"[{time.strftime('%X')}] ✅ {label} ({uid}) successfully injected.")
        else:
            print(f"[{time.strftime('%X')}] ⚠️ Failed to inject {label}. Status Code: {response.status_code}")
    except Exception as e:
        print(f"[{time.strftime('%X')}] ❌ Error during injection: {e}")

def bot_logic():
    url = "http://new.sensix.shop:2011/user_update_uid"
    
    # ENV theke cookie collect kora hocche
    session_cookie = os.environ.get("SESSION_COOKIE")
    
    if not session_cookie:
        print("❌ Error: ENV te 'SESSION_COOKIE' pawa jani! Prothome ENV set korun.")
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"session={session_cookie}"
    }

    main_uid = "2731370681"
    remove_uid = "27313706811"

    # ১. RUN KORAR SATHE SATHE MAIN UID ADD KORBE
    print("🚀 Bot started! Injecting Main UID immediately...")
    inject_uid(url, headers, main_uid, "Main UID")

    while True:
        try:
            # ২. 2 MIN POR POR LOOP CHOLBE
            print("Sleeping for 2 minutes before the next cycle...")
            time.sleep(120)  # 120 seconds = 2 minutes

            # ৩. REMOVE UID ADD KORE AGER TA AUTO REMOVE KORBE
            print("Triggering removal cycle...")
            inject_uid(url, headers, remove_uid, "Remove UID")

            # Shate shate back to back request jate server crash na kore tar jonno 1 sec gap
            time.sleep(1)

            # ৪. SATHE SATHE ABR MAIN UID ADD KORE DIBE
            inject_uid(url, headers, main_uid, "Main UID")

            # SELF PING (Jodi hosting-er public URL thake)
            self_url = os.environ.get("SELF_URL")
            if self_url:
                try:
                    requests.get(self_url)
                    print("⚡ Self-ping sent successfully.")
                except:
                    pass

        except Exception as loop_error:
            print(f"Loop error occurred: {loop_error}")
            time.sleep(5) # error khele 5 sec por abr try korbe

if __name__ == "__main__":
    # Web server-ke alada thread-e start kora hocche jate sleeping a na jai
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    # Main bot loop start
    bot_logic()
