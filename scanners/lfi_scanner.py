import requests
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

COOKIES = {
    "security": "low",
}

def load_payloads(file_path="lfi.txt"):
    file_path = r"D:/GitHub/web-crawler/scanners/lfi.txt"  # ✅ تأكد إن المسار دا فعلاً صح
    if not os.path.exists(file_path):
        print(f"[-] Payload file not found: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"[⚠️] Error reading payload file: {e}")
        return []

def check_lfi(target_url, payload):
    target = f"{target_url}{payload}"
    try:
        response = requests.get(target, headers=HEADERS, cookies=COOKIES, timeout=5)

        if response.status_code == 200 and "root:x:0:0:" in response.text:
            return {
                "status": True,
                "payload": payload,
                "details": f"Potential LFI at {target}"
            }

    except requests.RequestException as e:
        return {
            "status": False,
            "details": f"Request error: {e}"
        }

    return None

def scan_lfi(target_url):
    payloads = load_payloads()
    if not payloads:
        return {
            "status": False,
            "details": "No payloads loaded."
        }

    found_payloads = []
    details = []

    for payload in payloads:
        result = check_lfi(target_url, payload)
        if result and result.get("status"):
            found_payloads.append(result["payload"])
            details.append(result["details"])

    if found_payloads:
        return {
            "status": True,
            "payloads": found_payloads,
            "details": "; ".join(details)
        }
    else:
        return {
            "status": False,
            "details": "No LFI vulnerabilities detected."
        }

# ✅ Optional: for standalone testing
if __name__ == "__main__":
    target_url = input("[?] Enter URL (e.g., http://127.0.0.1/DVWA/vulnerabilities/fi/?page=): ").strip()

    if "?page=" not in target_url:
        print("[!] URL must contain '?page=' for scanning.")
    else:
        result = scan_lfi(target_url)
        print("\nScan Result:\n", result)
