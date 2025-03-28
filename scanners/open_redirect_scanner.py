import requests
import urllib.parse

def load_payloads(file_path="open_redirect.txt"):
    """ تحميل الـ Payloads من ملف خارجي """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"[-] Payload file not found: {file_path}")
        return []

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

COOKIES = {
    "security": "low"
}

def check_open_redirect(target_url, payload):
    """ فحص Open Redirect باستخدام الـ Payloads """
    parsed_url = urllib.parse.urlparse(target_url)
    query = urllib.parse.parse_qs(parsed_url.query)
    
    for param in query:
        test_url = f"{target_url}&{param}={urllib.parse.quote(payload)}"
        print(f"[🔍] Testing: {test_url}")

        try:
            response = requests.get(test_url, headers=HEADERS, cookies=COOKIES, allow_redirects=False, timeout=5)
            
            if response.status_code in [301, 302] and payload in response.headers.get("Location", ""):
                print(f"\n[✅] Open Redirect Found: {test_url}")
                print(f"[➡️] Redirected To: {response.headers['Location']}\n")
            else:
                print("[❌] Not Vulnerable")
                print(f"[📄] Response Content:\n{response.text[:200]}\n{'-' * 80}")

        except requests.RequestException as e:
            print(f"[⚠️] Error: {e}")

def scan_open_redirect(target_url):
    """ تشغيل فحص Open Redirect """
    payloads = load_payloads()
    if not payloads:
        print("[-] No payloads loaded. Exiting...")
        return

    print("\n[+] Starting Open Redirect Scan...\n")
    for payload in payloads:
        check_open_redirect(target_url, payload)
    print("\n[✅] Scan Completed!")

if __name__ == "__main__":
    target_url = input("[?] Enter URL (e.g., http://127.0.0.1/DVWA/vulnerabilities/redirect/?page=): ").strip()
    
    if "?" not in target_url:
        print("[!] Ensure the URL has a query parameter for testing.")
    else:
        scan_open_redirect(target_url)
