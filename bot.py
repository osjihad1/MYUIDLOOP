def auto_login(username, password):
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
