import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

# تحميل الـ payloads من ملف xss.txt
def load_payloads(file_path="xss.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"[-] Payload file not found: {file_path}")
        return []

# استخراج كل الـ forms من الصفحة
def get_all_forms(url):
    soup = bs(requests.get(url).content, "html.parser")
    return soup.find_all("form")

# استخراج تفاصيل الـ form
def get_form_details(form):
    details = {}
    action = form.attrs.get("action", "").lower()
    method = form.attrs.get("method", "get").lower()
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        inputs.append({"type": input_type, "name": input_name})
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

# إرسال البيانات للفورم
def submit_form(form_details, url, value):
    target_url = urljoin(url, form_details["action"])
    inputs = form_details["inputs"]
    data = {}

    for input in inputs:
        if input["type"] == "text" or input["type"] == "search":
            input["value"] = value
        input_name = input.get("name")
        input_value = input.get("value")
        if input_name and input_value:
            data[input_name] = input_value

    if form_details["method"] == "post":
        return requests.post(target_url, data=data)
    else:
        return requests.get(target_url, params=data)

# فحص XSS
def scan_xss(url):
    forms = get_all_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")
    
    payloads = load_payloads()  # تحميل الـ payloads من ملف xss.txt
    if not payloads:
        print("[-] No payloads loaded.")
        return False

    is_vulnerable = False
    for form in forms:
        form_details = get_form_details(form)
        for payload in payloads:
            content = submit_form(form_details, url, payload).content.decode()
            if payload in content:
                print(f"[+] XSS Detected on {url}")
                print(f"[*] Form details:")
                pprint(form_details)
                is_vulnerable = True
                break  # وقف التجربة بعد أول اكتشاف للثغرة على الفورم

    return is_vulnerable

# تشغيل الفحص بناءً على إدخال المستخدم
if __name__ == "__main__":
    target_url = input("[+] Enter target URL: ").strip()  # يطلب من المستخدم إدخال URL
    if target_url:
        scan_xss(target_url)
    else:
        print("[-] No URL provided. Exiting...")
