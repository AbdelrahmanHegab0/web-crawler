from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanners.crawler import crawl_page
from scanners.lfi_scanner import scan_lfi
from scanners.xss_scanner import scan_xss
from scanners.open_redirect_scanner import scan_open_redirect

app = FastAPI()

# ✅ إعدادات CORS الصحيحة

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:5500/",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"message": "Welcome to the Web Vulnerability Scanner API!"}

@app.get("/crawl")
def start_crawl(url: str):
    result = crawl_page(url)
    return {"crawl_results": result}

@app.post("/scan/lfi")
def scan_for_lfi(data: ScanRequest):
    return {"LFI Scan Result": scan_lfi(data.url)}

@app.post("/scan/xss")
def scan_for_xss(data: ScanRequest):
    return {"XSS Scan Result": scan_xss(data.url)}

@app.post("/scan/open_redirect")
def scan_for_open_redirect(data: ScanRequest):
    return {"Open Redirect Scan Result": scan_open_redirect(data.url)}

@app.post("/scan/full")
def full_scan(data: ScanRequest):
    crawl_results = crawl_page(data.url)
    scan_results = []

    if "error" in crawl_results:
        return {"error": "Crawling failed. No URLs to scan."}

    for link in crawl_results.get("links", []):
        scan_results.append({
            "url": link,
            "XSS": scan_xss(link),
            "LFI": scan_lfi(link),
            "Open Redirect": scan_open_redirect(link)
        })
    return {"Full Scan Results": scan_results}
