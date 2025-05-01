from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanners.crawler import crawl_page
from scanners.lfi_scanner import scan_lfi
from scanners.xss_scanner import scan_xss
from scanners.open_redirect_scanner import scan_open_redirect
import io
import requests
from collections import defaultdict  # 🚀

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str
    scanners: list[str]

@app.get("/")
def home():
    return {"message": "Welcome to the Web Vulnerability Scanner API!"}

# 🚀 دالة توليد Tree View من قائمة روابط
class Node:
    def __init__(self):
        self.children = defaultdict(Node)

    def insert(self, parts):
        if parts:
            self.children[parts[0]].insert(parts[1:])

    def to_string(self, level=0):
        result = ""
        for key in sorted(self.children):
            result += "│   " * level + "├── " + key + "\n"
            result += self.children[key].to_string(level + 1)
        return result

def build_url_tree(urls):
    tree = Node()
    for url in urls:
        parts = url.strip("/").split("/")
        tree.insert(parts)
    return tree.to_string()

@app.post("/scan/")
def scan_website(data: ScanRequest):
    crawl_results = crawl_page(data.url)
    selected_scanners = data.scanners
    scan_results = []

    links_to_scan = []
    if "error" in crawl_results or not crawl_results.get("links"):
        links_to_scan = [data.url]
    else:
        links_to_scan = crawl_results.get("links", [])

    for link in links_to_scan:
        result = {"url": link}

        if "xss" in selected_scanners:
            xss_result = scan_xss(link)
            result["XSS"] = xss_result if xss_result else "No XSS vulnerabilities detected"

        if "lfi" in selected_scanners:
            lfi_result = scan_lfi(link)
            result["LFI"] = lfi_result if lfi_result else "No LFI vulnerabilities detected"

        if "redirect" in selected_scanners:
            redirect_result = scan_open_redirect(link)
            result["Open Redirect"] = redirect_result if redirect_result else "No Open Redirect vulnerabilities detected"

        scan_results.append(result)

    payloads_used = []
    if "xss" in selected_scanners:
        payloads_used.append("XSS Payloads")
    if "lfi" in selected_scanners:
        payloads_used.append("LFI Payloads")
    if "redirect" in selected_scanners:
        payloads_used.append("Redirect Payloads")

    report_content = f"==============================\n"
    report_content += f"\U0001F575️ Vulnerability Report\n"
    report_content += f"==============================\n\n"
    report_content += f"\U0001F310 Target Domain:\n{data.url}\n\n"
    report_content += f"Scanners Used: {', '.join(selected_scanners)}\n"
    report_content += f"Payloads Used: {', '.join(payloads_used)}\n\n"

    for result in scan_results:
        report_content += f"------------------------------\n"
        report_content += f"\U0001F50D Vulnerable URL:\n{result['url']}\n"
        
        if 'XSS' in result:
            report_content += f"\n\U0001F511 XSS:\n{result['XSS']}\n"
        
        if 'LFI' in result:
            lfi_result = result.get('LFI', {})
            if lfi_result["status"]:
                report_content += f"\n\U0001F511 LFI:\nFound with payloads: {', '.join(lfi_result['payloads'])}\nDetails: {lfi_result['details']}\n"
            else:
                report_content += f"\n\U0001F511 LFI:\n{lfi_result['details']}\n"
        
        if 'Open Redirect' in result:
            redirect_result = result.get('Open Redirect', {})
            if redirect_result["status"]:
                report_content += f"\n\U0001F511 Open Redirect:\nRedirected to: {', '.join(redirect_result['redirects'])}\nDetails: {redirect_result['details']}\n"
            else:
                report_content += f"\n\U0001F511 Open Redirect:\n{redirect_result['details']}\n"

        report_content += f"\n"

    # 🚀 إضافة الشجرة النصية بعد الفحص
    if links_to_scan and links_to_scan != [data.url]:
        report_content += "==============================\n"
        report_content += "\U0001F4C2 Site Structure (Tree View)\n"
        report_content += "==============================\n"
        tree_view = build_url_tree(links_to_scan)
        report_content += tree_view + "\n"

    report_file = io.StringIO(report_content)
    response = Response(content=report_file.getvalue(), media_type="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=scan_report.txt"
    return response
