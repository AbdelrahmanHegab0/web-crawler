from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanners.crawler import crawl_page
from scanners.lfi_scanner import scan_lfi
from scanners.xss_scanner import scan_xss
from scanners.open_redirect_scanner import scan_open_redirect
import io

app = FastAPI()

# إعدادات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 بيانات الريكوست
class ScanRequest(BaseModel):
    url: str
    scanners: list[str]  # ["xss", "lfi", "redirect"] or ["all"]

@app.get("/")
def home():
    return {"message": "Welcome to the Web Vulnerability Scanner API!"}

@app.post("/scan/")
def scan_website(data: ScanRequest):
    # 🕷️ Step 1: Crawl first
    crawl_results = crawl_page(data.url)

    # التحقق من وجود روابط من الكراول
    if "error" in crawl_results or not crawl_results.get("links"):
        return {"error": "Crawling failed or no URLs found to scan."}

    selected_scanners = data.scanners
    scan_results = []

    # فحص الروابط باستخدام الأدوات المختارة
    for link in crawl_results.get("links", []):
        result = {"url": link}

        if "all" in selected_scanners or "xss" in selected_scanners:
            xss_result = scan_xss(link)
            result["XSS"] = xss_result if xss_result else "No XSS vulnerabilities detected"

        if "all" in selected_scanners or "lfi" in selected_scanners:
            lfi_result = scan_lfi(link)
            result["LFI"] = lfi_result if lfi_result else "No LFI vulnerabilities detected"

        if "all" in selected_scanners or "redirect" in selected_scanners:
            redirect_result = scan_open_redirect(link)
            result["Open Redirect"] = redirect_result if redirect_result else "No Open Redirect vulnerabilities detected"

        scan_results.append(result)

    # جمع معلومات الـ payloads المستخدمة
    payloads_used = []
    if "all" in selected_scanners or "xss" in selected_scanners:
        payloads_used.append("XSS Payloads")
    if "all" in selected_scanners or "lfi" in selected_scanners:
        payloads_used.append("LFI Payloads")
    if "all" in selected_scanners or "redirect" in selected_scanners:
        payloads_used.append("Redirect Payloads")
    
    # توليد محتوى التقرير بصيغة نصية
    report_content = f"Scan Report for {data.url}\n\n"
    report_content += f"Scanners Used: {', '.join(selected_scanners)}\n"
    report_content += f"Payloads Used: {', '.join(payloads_used)}\n\n"

    for result in scan_results:
        report_content += f"URL: {result['url']}\n"
        if 'XSS' in result:
            report_content += f"  XSS: {result['XSS']}\n"
        if 'LFI' in result:
            report_content += f"  LFI: {result['LFI']}\n"
        if 'Open Redirect' in result:
            report_content += f"  Open Redirect: {result['Open Redirect']}\n"
        report_content += "\n"

    # إنشاء ملف .txt في الذاكرة
    report_file = io.StringIO(report_content)
    response = Response(content=report_file.getvalue(), media_type="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=scan_report.txt"
    return response
