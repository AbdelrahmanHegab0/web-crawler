from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanners.crawler import crawl_page
from scanners.lfi_scanner import scan_lfi
from scanners.xss_scanner import scan_xss
from scanners.open_redirect_scanner import scan_open_redirect
import io
from collections import defaultdict
from urllib.parse import urlparse


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
    scanners: list[str] = []
    report_type: str = "both"  # 'vulnerabilities', 'structure', or 'both'

@app.get("/")
def home():
    return {"message": "Welcome to the Web Vulnerability Scanner API!"}

class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []

    def to_dict(self):
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children]
        }

def build_tree_json(urls):
    root = TreeNode("root")
    nodes = {"root": root}
    for url in urls:
        parts = url.strip("/").split("/")
        current = root
        path = ""
        for part in parts:
            path += "/" + part
            if path not in nodes:
                new_node = TreeNode(part)
                current.children.append(new_node)
                nodes[path] = new_node
            current = nodes[path]
    return root.to_dict()

@app.get("/site-tree/")
async def get_site_tree(url: str):
    site_tree = crawl_page(url)
    return {"name": url, "children": site_tree}

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
        parsed = urlparse(url)
        netloc = parsed.netloc
        scheme = parsed.scheme
        path_parts = list(filter(None, parsed.path.strip("/").split("/")))
        
        full_parts = [scheme + ":"] if scheme else []
        if netloc:
            full_parts.append(netloc)
        full_parts.extend(path_parts)

        tree.insert(full_parts)
    return tree.to_string()

def generate_structure_report(url, links):
    report_content = (
        "==============================\n"
        "📂 Site Structure (Tree View)\n"
        "==============================\n"
    )
    if links and links != [url]:
        tree_view = build_url_tree(links)
        report_content += tree_view
    else:
        report_content += "No links found to display tree structure.\n"
    report_content += "==============================\n"
    return report_content


def generate_vulnerability_report(url, links, selected_scanners):
    scan_results = []
    payloads_used = set()

    for link in links:
        result = {"url": link}
        if "xss" in selected_scanners:
            xss_result = scan_xss(link)
            result["XSS"] = xss_result if xss_result else "❌ No XSS vulnerabilities detected"
            payloads_used.add("XSS Payloads")
        if "lfi" in selected_scanners:
            lfi_result = scan_lfi(link)
            result["LFI"] = lfi_result if lfi_result else "❌ No LFI vulnerabilities detected"
            payloads_used.add("LFI Payloads")
        if "redirect" in selected_scanners:
            redirect_result = scan_open_redirect(link)
            result["Open Redirect"] = redirect_result if redirect_result else "❌ No Open Redirect vulnerabilities detected"
            payloads_used.add("Redirect Payloads")
        scan_results.append(result)

    report_content = (
        "==============================\n"
        "🛡️  Vulnerability Report\n"
        "==============================\n\n"
        f"🌐 Target Domain: {url}\n"
        f"🧪 Scanners Used: {', '.join(selected_scanners) if selected_scanners else 'None'}\n"
        f"💣 Payloads Used: {', '.join(payloads_used) if payloads_used else 'None'}\n\n"
    )

    for result in scan_results:
        report_content += "------------------------------\n"
        report_content += f"🔗 URL: {result['url']}\n"
        
        # Handle XSS Vulnerability
        if 'XSS' in result:
            xss_data = result['XSS']
            if isinstance(xss_data, dict) and xss_data.get("status"):
                report_content += (
                    f"   🔸 XSS: ✅ Found!\n"
                    f"       • Payloads: {', '.join(xss_data['payloads'])}\n"
                    f"       • Details: {xss_data['details']}\n"
                )
            else:
                report_content += f"   🔸 XSS: {xss_data}\n"
        
        # Handle LFI Vulnerability
        if 'LFI' in result:
            lfi_data = result['LFI']
            if isinstance(lfi_data, dict) and lfi_data.get("status"):
                report_content += (
                    f"   🔸 LFI: ✅ Found!\n"
                    f"       • Payloads: {', '.join(lfi_data['payloads'])}\n"
                    f"       • Details: {lfi_data['details']}\n"
                )
            else:
                report_content += f"   🔸 LFI: {lfi_data}\n"
        
        # Handle Open Redirect Vulnerability
        if 'Open Redirect' in result:
            redir_data = result['Open Redirect']
            if isinstance(redir_data, dict) and redir_data.get("status"):
                report_content += (
                    f"   🔸 Open Redirect: ✅ Found!\n"
                    f"       • Redirects: {', '.join(redir_data['redirects'])}\n"
                    f"       • Details: {redir_data['details']}\n"
                )
            else:
                report_content += f"   🔸 Open Redirect: {redir_data}\n"
        
        report_content += "\n"

    report_content += "==============================\n"
    return report_content



@app.post("/crawl_only")
async def crawl_only(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"error": "No URL provided"}

    crawl_results = crawl_page(url)
    links = crawl_results.get("links", [])
    if not links:
        return {"error": "No links found"}

    report_content = generate_structure_report(url, links)
    report_file = io.StringIO(report_content)
    response = Response(content=report_file.getvalue(), media_type="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=site_structure.txt"
    return response

@app.post("/scan/")
def scan_website(data: ScanRequest):
    # نفّذ الكراولينج بس
    crawl_results = crawl_page(data.url)
    links_to_scan = [data.url] if "error" in crawl_results or not crawl_results.get("links") else crawl_results.get("links", [])
    report_content = ""

    # لو structure بس، نفّذ الـ Tree Report بس بدون أي حاجة متعلقة بالثغرات
    if data.report_type == "structure":
        report_content = generate_structure_report(data.url, links_to_scan)
    # لو vulnerabilities بس، نفّذ الـ Vulnerability Report بس
    elif data.report_type == "vulnerabilities":
        if not data.scanners:
            report_content = "Error: No scanners provided for vulnerabilities report.\n"
        else:
            report_content = generate_vulnerability_report(data.url, links_to_scan, data.scanners)
    # لو both، نفّذ الاتنين
    elif data.report_type == "both":
        report_content = generate_structure_report(data.url, links_to_scan)
        if data.scanners:
            report_content += "\n" + generate_vulnerability_report(data.url, links_to_scan, data.scanners)
        else:
            report_content += "\nNo scanners provided for vulnerabilities report.\n"
    else:
        report_content = "Error: Invalid report_type. Use 'structure', 'vulnerabilities', or 'both'.\n"

    report_file = io.StringIO(report_content)
    response = Response(content=report_file.getvalue(), media_type="text/plain")
    response.headers["Content-Disposition"] = f"attachment; filename={'site_structure' if data.report_type == 'structure' else 'scan_report'}.txt"
    return response