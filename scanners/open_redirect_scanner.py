import requests
import urllib.parse
import os

# ======= إعدادات الهدف =========
cookies = {
    "PHPSESSID": "PUT_YOUR_SESSION_ID_HERE",
    "security": "low"
}

# ======= تحميل البايلودات =========
def load_payloads(file_path="open_redirect.txt"):
    default_path = r"D:/GitHub/web-crawler/scanners/open_redirect.txt"
    file_path = file_path if os.path.exists(file_path) else default_path

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[⚠️] Error loading payloads: {e}")
        return []

# ======= فحص الثغرة =========
def check_open_redirect(target_url, payload):
    try:
        parsed_url = urllib.parse.urlparse(target_url)
        query = urllib.parse.parse_qs(parsed_url.query or "")

        if not query:
            common_params = ['redirect', 'url', 'next', 'goto', 'redir']
            for param in common_params:
                test_url = f"{target_url}?{param}={urllib.parse.quote(payload)}"
                try:
                    response = requests.get(test_url, cookies=cookies, allow_redirects=False, timeout=5)
                    location = response.headers.get("Location", "")
                    if response.status_code in [301, 302, 307] and payload in urllib.parse.unquote(location):
                        return {
                            "status": True,
                            "payload": payload,
                            "url": test_url,
                            "redirected_to": location,
                            "details": f"Open Redirect found: {test_url} → {location}"
                        }
                except requests.RequestException:
                    continue
        else:
            for param in query:
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                params = query.copy()
                params[param] = [payload]
                test_url = f"{base_url}?{urllib.parse.urlencode(params, doseq=True)}"
                try:
                    response = requests.get(test_url, cookies=cookies, allow_redirects=False, timeout=5)
                    location = response.headers.get("Location", "")
                    if response.status_code in [301, 302, 307] and payload in urllib.parse.unquote(location):
                        return {
                            "status": True,
                            "payload": payload,
                            "url": test_url,
                            "redirected_to": location,
                            "details": f"Open Redirect found: {test_url} → {location}"
                        }
                except requests.RequestException:
                    continue

    except Exception as e:
        print(f"[!] Error in check_open_redirect: {e}")

    return None

# ======= الفحص النهائي =========
def scan_open_redirect(target_url, payload_file="open_redirect.txt"):
    if not target_url:
        return {
            "status": False,
            "redirects": [],
            "details": "No URL provided."
        }

    payloads = load_payloads(payload_file)
    if not payloads:
        return {
            "status": False,
            "redirects": [],
            "details": "No payloads loaded."
        }

    if not target_url.startswith(("http://", "https://")):
        target_url = "http://" + target_url

    for payload in payloads:
        result = check_open_redirect(target_url, payload)
        if result and result.get("status"):
            return {
                "status": True,
                "payload": result["payload"],
                "url": result["url"],
                "redirected_to": result["redirected_to"],
                "redirects": [result["url"]],  # ✅ Added for compatibility
                "details": result["details"]
            }

    return {
        "status": False,
        "redirects": [],
        "details": "No Open Redirect vulnerabilities found."
    }

# ======= للاختبار المباشر =========
if __name__ == "__main__":
    target_url = input("[?] Enter URL (e.g., http://127.0.0.1/DVWA/vulnerabilities/redirect/): ").strip()

    if not target_url:
        print("[!] You must provide a URL.")
    else:
        result = scan_open_redirect(target_url)
        print("\nScan Result:\n", result)
