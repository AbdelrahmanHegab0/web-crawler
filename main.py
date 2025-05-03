from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanners.crawler import crawl_page
from scanners.lfi_scanner import scan_lfi
from scanners.xss_scanner import scan_xss
from scanners.open_redirect_scanner import scan_open_redirect
import io
from collections import defaultdict

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
        parts = url.strip("/").split("/")
        tree.insert(parts)
    return tree.to_string()


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

    tree_view = build_url_tree(links)

    report_content = f"==============================\n"
    report_content += f"📂 Website Structure Report\n"
    report_content += f"==============================\n\n"
    report_content += f"Target: {url}\n\n"
    report_content += tree_view + "\n"

    report_file = io.StringIO(report_content)
    response = Response(content=report_file.getvalue(),
                        media_type="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=site_structure.txt"
    return response


@app.post("/scan/")
def scan_website(data: ScanRequest):
    crawl_results = crawl_page(data.url)

    # Run scans (optional, but not included in the report)
    selected_scanners = data.scanners
    scan_results = []
    links_to_scan = []

    if "error" in crawl_results or not crawl_results.get("links"):
        links_to_scan = [data.url]
    else:
        links_to_scan = crawl_results.get("links", [])

    # Generate minimal report (target domain + tree structure only)
    report_content = "==============================\n"
    report_content += "🕵️ Vulnerability Report\n"
    report_content += "==============================\n\n"
    report_content += f"🌐 Target Domain:\n{data.url}\n\n"

    # Add tree structure section
    report_content += "==============================\n"
    report_content += "📂 Site Structure (Tree View)\n"
    report_content += "==============================\n"

    if links_to_scan and links_to_scan != [data.url]:
        tree_view = build_url_tree(links_to_scan)
        report_content += tree_view + "\n"
    else:
        report_content += "No links found to display tree structure.\n"

    report_file = io.StringIO(report_content)
    response = Response(content=report_file.getvalue(),
                        media_type="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=scan_report.txt"
    return response
