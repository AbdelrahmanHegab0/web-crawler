from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

app = FastAPI()

class ScanRequest(BaseModel):
    target_url: str

def get_all_forms(url):
    soup = bs(requests.get(url).content, "html.parser")
    return soup.find_all("form")

def get_form_details(form):
    details = {}
    action = form.attrs.get("action").lower()
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

def scan_xss(url):
    forms = get_all_forms(url)
    js_script = "<Script>alert('hi')</scripT>"
    vulnerabilities = []
    for form in forms:
        form_details = get_form_details(form)
        content = submit_form(form_details, url, js_script).content.decode()
        if js_script in content:
            vulnerabilities.append(form_details)
    return vulnerabilities

def scan_lfi(url):
    payloads = ["../../../../etc/passwd", "..%2F..%2F..%2F..%2Fetc/passwd"]
    vulnerable = []
    for payload in payloads:
        lfi_url = f"{url}?file={payload}"
        response = requests.get(lfi_url)
        if "root:x:" in response.text:
            vulnerable.append(lfi_url)
    return vulnerable

def scan_open_redirect(url):
    payloads = [
        "http://evil.com", "//evil.com", "/\\evil.com", "//\\evil.com"
    ]
    vulnerable = []
    for payload in payloads:
        redirect_url = f"{url}?next={payload}"
        response = requests.get(redirect_url, allow_redirects=False)
        if response.status_code in [301, 302] and payload in response.headers.get("Location", ""):
            vulnerable.append(redirect_url)
    return vulnerable

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vulnerability Scanner!"}

@app.post("/scan/xss")
def xss_scan(request: ScanRequest):
    vulnerabilities = scan_xss(request.target_url)
    if not vulnerabilities:
        return {"result": "No XSS vulnerabilities found."}
    return {"vulnerabilities": vulnerabilities}

@app.post("/scan/lfi")
def lfi_scan(request: ScanRequest):
    vulnerabilities = scan_lfi(request.target_url)
    if not vulnerabilities:
        return {"result": "No LFI vulnerabilities found."}
    return {"vulnerabilities": vulnerabilities}

@app.post("/scan/open_redirect")
def open_redirect_scan(request: ScanRequest):
    vulnerabilities = scan_open_redirect(request.target_url)
    if not vulnerabilities:
        return {"result": "No Open Redirect vulnerabilities found."}
    return {"vulnerabilities": vulnerabilities}
