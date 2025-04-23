import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, urlunparse

# ✅ Normalize user input (e.g. add https:// and www.)
def normalize_url(url):
    pattern = r"^(https?://)?(www\.)?(\w+\.\w+)\w*"
    url = re.sub(pattern, r"https://www.\3", url)
    return url

# ✅ Normalize full URL (strip query and fragment)
def normalize_full_url(full_url):
    parsed = urlparse(full_url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip('/'), '', '', ''))

# ✅ Simple valid URL checker
def is_valid_url(url):
    pattern = r"^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?$"
    return re.match(pattern, url) is not None

# ✅ Request with user-agent header
def fetch_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)'}
    try:
        print(f"[*] Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching page: {e}")
        return None

# ✅ Crawl a page and extract links, scripts, and images
def crawl_page(url):
    seen_urls = set()
    url = normalize_url(url)
    response = fetch_page(url)

    if not response:
        return {"error": "Failed to fetch the page"}

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = response.url

    found_links = []
    found_scripts = []
    found_images = []

    # 🔗 Extract <a href="">
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href.startswith(('javascript:', '#')):
            full_url = normalize_full_url(urljoin(base_url, href))
            if full_url not in seen_urls and is_valid_url(full_url):
                seen_urls.add(full_url)
                found_links.append(full_url)

    # 📜 Extract <script src="">
    for script in soup.find_all('script', src=True):
        full_script = normalize_full_url(urljoin(base_url, script['src']))
        if is_valid_url(full_script):
            found_scripts.append(full_script)

    # 🖼️ Extract <img src="">
    for img in soup.find_all('img', src=True):
        full_img = normalize_full_url(urljoin(base_url, img['src']))
        if is_valid_url(full_img):
            found_images.append(full_img)

    return {
        "links": found_links,
        "scripts": found_scripts,
        "images": found_images
    }
