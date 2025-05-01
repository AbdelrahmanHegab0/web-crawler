import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import os
import time
from tenacity import retry, stop_after_attempt, wait_fixed

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def load_payloads(file_path=None):
    # Same behavior as your LFI scanner
    file_path = file_path or r"D:/GitHub/web-crawler/scanners/xss.txt"
    
    if not os.path.exists(file_path):
        print(f"[-] Payload file not found: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"[⚠️] Error reading payload file: {e}")
        return []

def get_all_forms(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = bs(response.content, "html.parser")
        return soup.find_all("form")
    except Exception as e:
        print(f"[-] Error fetching forms from {url}: {e}")
        return []

def get_form_details(form):
    details = {
        "action": form.attrs.get("action", "").lower(),
        "method": form.attrs.get("method", "get").lower(),
        "inputs": []
    }
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        details["inputs"].append({"type": input_type, "name": input_name})
    return details

def submit_form(form_details, url, value):
    target_url = urljoin(url, form_details["action"])
    inputs = form_details["inputs"]
    data = {}

    for input in inputs:
        if input["type"] in ["text", "search"]:
            input["value"] = value
        input_name = input.get("name")
        input_value = input.get("value")
        if input_name and input_value:
            data[input_name] = input_value

    try:
        if form_details["method"] == "post":
            return requests.post(target_url, data=data, headers=HEADERS, timeout=10)
        else:
            return requests.get(target_url, params=data, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"[-] Error submitting form: {e}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def check_xss_vulnerability(url, form_details, payload):
    response = submit_form(form_details, url, payload)
    if response and payload in response.text:
        return True
    return False

def scan_xss(target_url, payload_file=None):
    payloads = load_payloads(payload_file)
    if not payloads:
        return {
            "status": False,
            "details": "No payloads loaded."
        }

    if not target_url.startswith(("http://", "https://")):
        target_url = "http://" + target_url

    forms = get_all_forms(target_url)
    if not forms:
        return {
            "status": False,
            "details": "No forms found on the target page."
        }

    found_payloads = []
    for form in forms:
        form_details = get_form_details(form)
        for payload in payloads:
            try:
                if check_xss_vulnerability(target_url, form_details, payload):
                    found_payloads.append(payload)
                    break
            except Exception as e:
                print(f"[⚠️] Error: {e}")
                time.sleep(1)

    if found_payloads:
        return {
            "status": True,
            "payloads": found_payloads,
            "details": f"Potential XSS vulnerability(ies) detected using {len(found_payloads)} payload(s)."
        }
    else:
        return {
            "status": False,
            "details": "No XSS vulnerabilities detected."
        }

# ✅ Optional: for standalone testing
if __name__ == "__main__":
    target_url = input("[?] Enter target URL (e.g., http://127.0.0.1/DVWA/vulnerabilities/xss_r/): ").strip()
    payload_path = input("[?] Path to XSS payloads file (default is hardcoded path): ").strip()
    payload_path = payload_path if payload_path else None

    result = scan_xss(target_url, payload_path)
    print("\nScan Result:\n", result)
