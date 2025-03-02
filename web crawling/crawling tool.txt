import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, urlunparse

# Function to normalize and correct the URL
def normalize_url(url):
    # Define a regex pattern to detect and fix common URL typos
    pattern = r"(https?://)?(www\.)?(\w+\.\w+)\w*"
    # Ensure the URL starts with http/https and normalize the domain
    url = re.sub(pattern, r"https://www.\3", url)
    return url

# Function to normalize full URLs (remove fragments, query strings)
def normalize_full_url(full_url):
    parsed = urlparse(full_url)
    normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))  # Strip query and fragment
    print(normalized)
    return normalized

# Function to check if a URL is valid
def is_valid_url(url):
    pattern = r"^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?$"
    return re.match(pattern, url) is not None

# Function to fetch and parse a webpage
def fetch_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)'}  # Set a user-agent header
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

# Main function to perform crawling
def crawl_page(url):
    seen_urls = set()  # Track visited URLs to avoid duplicates

    # Normalize the URL
    url = normalize_url(url)
    response = fetch_page(url)

    if response:
        # Parse the content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = response.url  # Base URL to resolve relative links

        # Output 1: Extract all URLs from links on the page
        print("All valid URLs from links on the page:")
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href and not href.startswith(('javascript', '#')):  # Ignore JS links and fragments
                full_url = urljoin(base_url, href)  # Handle relative links
                normalized_url = normalize_full_url(full_url)
                if normalized_url not in seen_urls and is_valid_url(normalized_url):
                    seen_urls.add(normalized_url)
                    print(normalized_url)

        # Output 2: Extract all JavaScript files
        print("\nJavaScript files:")
        scripts = soup.find_all('script')
        for script in scripts:
            js_file = script.get('src')
            if js_file:
                full_js_file = urljoin(base_url, js_file)  # Handle relative JS files
                if is_valid_url(full_js_file):
                    print(full_js_file)

        # Output 3: Extract all image files
        print("\nImages:")
        images = soup.find_all('img')
        for img in images:
            img_file = img.get('src')
            if img_file:
                full_img_file = urljoin(base_url, img_file)  # Handle relative image files
                if is_valid_url(full_img_file):
                    print(full_img_file)


# Get the URL input from the user
url_input = input("Enter the URL: ")
crawl_page(url_input)