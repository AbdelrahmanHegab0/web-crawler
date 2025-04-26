import requests
import urllib.parse
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

COOKIES = {
    "security": "low"
}

def load_payloads(file_path=None):
    if file_path is None:
        file_path = r"D:\GitHub\web-crawler\scanners\open_redirect.txt"  # ✅ عدل المسار لو في مكان مختلف

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"[-] Payload file not found: {file_path}")
        return []

def check_open_redirect(target_url, payload):
    parsed_url = urllib.parse.urlparse(target_url)
    query = urllib.parse.parse_qs(parsed_url.query)

    vulnerable_urls = []
    
    for param in query:
        test_url = f"{target_url}&{param}={urllib.parse.quote(payload)}"

        try:
            response = requests.get(test_url, headers=HEADERS, cookies=COOKIES, allow_redirects=False, timeout=5)

            location = response.headers.get("Location", "")
            if response.status_code in [301, 302] and payload in location:
                vulnerable_urls.append({
                    "payload": payload,
                    "url": test_url,
                    "redirected_to": location
                })

        except requests.RequestException as e:
            return {
                "status": False,
                "details": f"Request error: {e}"
            }

    return vulnerable_urls

def scan_open_redirect(target_url):
    payloads = load_payloads()
    if not payloads:
        return {
            "status": False,
            "details": "No payloads loaded."
        }

    found = []

    for payload in payloads:
        result = check_open_redirect(target_url, payload)
        if result:
            found.extend(result)

    if found:
        formatted = [f"{item['url']} ➡ {item['redirected_to']}" for item in found]
        return {
            "status": True,
            "payloads": [item["payload"] for item in found],
            "details": "; ".join(formatted)
        }
    else:
        return {
            "status": False,
            "details": "No Open Redirect vulnerabilities detected."
        }

# ✅ Optional: For standalone testing
if __name__ == "__main__":
    target_url = input("[?] Enter URL (e.g., http://127.0.0.1/DVWA/vulnerabilities/redirect/?page=): ").strip()

    if "?" not in target_url:
        print("[!] Ensure the URL has a query parameter for testing.")
    else:
        result = scan_open_redirect(target_url)
        print("\nScan Result:\n", result)
