import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import time

BASE_URL = "https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2024/index.html"
DOWNLOAD_DIR = "data/ais_2024"

# Create folder if needed
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def is_data_file(url):
    return url.endswith((".zip", ".csv", ".gz"))


def get_all_file_links(base_url):
    print("Fetching index page...")
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")
    file_links = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue
        full_url = urljoin(base_url, href)
        if is_data_file(href):
            file_links.append(full_url)
        elif href.endswith("/"):
            # Recursively follow subfolders
            file_links.extend(get_all_file_links(full_url))

    return file_links


def download_file(url, dest_dir):
    local_filename = os.path.join(dest_dir, os.path.basename(url))
    if os.path.exists(local_filename):
        return  # Skip if already downloaded

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")


if __name__ == "__main__":
    all_links = get_all_file_links(BASE_URL)
    print(f"Found {len(all_links)} files to download.\n")

    for link in tqdm(all_links, desc="Downloading"):
        download_file(link, DOWNLOAD_DIR)
        # Add a small delay to avoid overwhelming the server
        time.sleep(5)

    print("\n✅ All files downloaded.")
    print(f"Files saved to: {DOWNLOAD_DIR}")
    print(f"Total files downloaded: {len(os.listdir(DOWNLOAD_DIR))}")
