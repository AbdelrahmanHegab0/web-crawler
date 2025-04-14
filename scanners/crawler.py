import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, urlunparse

# Function to normalize and correct the URL
def normalize_url(url):
    # Regular expression to ensure we add "https://" and "www."
    pattern = r"^(https?://)?(www\.)?(\w+\.\w+)\w*"
    url = re.sub(pattern, r"https://www.\3", url)
    return url

# Function to normalize full URLs (remove fragments, query strings)
def normalize_full_url(full_url):
    parsed = urlparse(full_url)
    # Strip out query and fragment part of the URL
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

# Function to check if a URL is valid
def is_valid_url(url):
    # Regular expression to check if the URL is valid
    pattern = r"^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?$"
    return re.match(pattern, url) is not None

# Function to fetch and parse a webpage
def fetch_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)'}
    try:
        print(f"[*] Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

# Function to perform crawling
def crawl_page(url):
    seen_urls = set()
    url = normalize_url(url)  # Normalize the URL first
    response = fetch_page(url)

    if not response:
        return {"error": "Failed to fetch the page"}

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = response.url

    found_links = []
    found_scripts = []
    found_images = []

    # Extract all URLs from links on the page
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href and not href.startswith(('javascript', '#')):  # Filter out JavaScript and anchor links
            full_url = urljoin(base_url, href)
            normalized_url = normalize_full_url(full_url)
            if normalized_url not in seen_urls and is_valid_url(normalized_url):
                seen_urls.add(normalized_url)
                found_links.append(normalized_url)

    # Extract all JavaScript files
    scripts = soup.find_all('script')
    for script in scripts:
        js_file = script.get('src')
        if js_file:
            full_js_file = urljoin(base_url, js_file)
            if is_valid_url(full_js_file):
                found_scripts.append(full_js_file)

    # Extract all image files
    images = soup.find_all('img')
    for img in images:
        img_file = img.get('src')
        if img_file:
            full_img_file = urljoin(base_url, img_file)
            if is_valid_url(full_img_file):
                found_images.append(full_img_file)

    return {
        "links": found_links,
        "scripts": found_scripts,
        "images": found_images
    }
