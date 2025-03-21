from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from pprint import pprint

# إنشاء التطبيق
app = FastAPI()

# نموذج البيانات للـ POST Request
class XSSRequest(BaseModel):
    target_url: str

# استخراج كل الفورمات في الصفحة
def get_all_forms(url):
    soup = bs(requests.get(url).content, "html.parser")
    return soup.find_all("form")

# استخراج تفاصيل الفورم
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

# تقديم البيانات للفورم
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

# XSS Scanner
def scan_xss(url):
    forms = get_all_forms(url)
    payload = "<script>alert('XSS')</script>"
    results = []
    for form in forms:
        form_details = get_form_details(form)
        response = submit_form(form_details, url, payload)
        if payload in response.text:
            results.append({
                "form": form_details,
                "vulnerable": True,
                "payload": payload
            })
        else:
            results.append({
                "form": form_details,
                "vulnerable": False
            })
    return results

# Home Endpoint
@app.get("/")
def home():
    return {"message": "Welcome to the Vulnerability Scanner!"}

# XSS Scanner Endpoint
@app.post("/scan/xss")
def xss_scanner(request: XSSRequest):
    url = request.target_url

    # التحقق من صحة الـ URL
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http or https.")

    results = scan_xss(url)
    return {
        "target": url,
        "results": results
    }
