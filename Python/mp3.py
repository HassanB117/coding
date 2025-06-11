import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import os
from urllib.parse import urljoin
from tqdm import tqdm
import time
import concurrent.futures
import threading # <--- NEW: Import threading for Lock

# --- Configuration ---
MAX_CONCURRENT_DOWNLOADS = 50 # You can adjust this number (e.g., 25 as requested)
                               # Be mindful of your internet speed and server limits.
DOWNLOAD_TIMEOUT_SECONDS = 120 # Timeout for each individual file download
INITIAL_URL_TIMEOUT_SECONDS = 40 # Timeout for initial directory listing fetch

# --- New Function for Single File Download ---
def download_single_file(file_info, url_base, download_folder, headers, overall_pbar, total_downloaded_bytes_lock):
    """
    Downloads a single file and updates progress.
    Returns (success_status, bytes_downloaded)
    """
    href = file_info['href']
    file_name = file_info['name']
    file_url = urljoin(url_base, href)
    file_path = os.path.join(download_folder, file_name)

    bytes_downloaded_this_file = 0
    success = False

    # Skip if file already exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        overall_pbar.write(f"Skipping download of {file_name} (already downloaded).")
        return True, 0 # Treat as success, no new bytes downloaded

    try:
        # Stream the download to get content in chunks
        file_response = requests.get(file_url, headers=headers, stream=True, timeout=DOWNLOAD_TIMEOUT_SECONDS)
        file_response.raise_for_status() # Check for HTTP errors like 404, 500

        total_size_in_bytes = int(file_response.headers.get('content-length', 0))

        with open(file_path, 'wb') as f, tqdm(
            total=total_size_in_bytes, unit='B', unit_scale=True, unit_divisor=1024,
            desc=f"Downloading {file_name}", initial=0, leave=False, position=1
        ) as pbar:
            for chunk in file_response.iter_content(chunk_size=81992): # Larger chunk size for efficiency
                if chunk: # Filter out keep-alive new chunks
                    f.write(chunk)
                    pbar.update(len(chunk))
                    bytes_downloaded_this_file += len(chunk)
        overall_pbar.write(f"Successfully downloaded: {file_name}")
        success = True

    except requests.exceptions.Timeout:
        overall_pbar.write(f"Error downloading {file_name}: Connection timed out after {DOWNLOAD_TIMEOUT_SECONDS} seconds.")
    except requests.exceptions.RequestException as e:
        overall_pbar.write(f"Error downloading {file_name}: {e}")
    except Exception as e:
        overall_pbar.write(f"An unexpected error occurred while downloading {file_name}: {e}")
    finally:
        if success:
            # The actual update of total_downloaded_bytes happens in the main loop
            # after the future completes, so no lock is needed here directly for the global counter
            pass

    return success, bytes_downloaded_this_file


# --- Main Download Logic (modified for concurrency) ---
def download_files_from_directory(url, download_folder="downloaded_files"):
    print(f"Attempting to download files from: {url}")

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"Created download folder: {download_folder}")
    else:
        print(f"Download folder already exists: {download_folder}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        response = requests.get(url, headers=headers, timeout=INITIAL_URL_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"Error accessing the URL: Connection to {url} timed out after {INITIAL_URL_TIMEOUT_SECONDS} seconds.")
        print("This often means the server is slow, busy, or your internet connection is unstable.")
        print("Please check your internet connection or try again later.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while accessing the URL: {e}")
        print("This could be a network issue, DNS problem, or the server refusing the connection.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')

    files_to_download_queue = []
    for link_element in links:
        if isinstance(link_element, Tag):
            href = link_element.get('href')
            if href and isinstance(href, str):
                file_name = os.path.basename(urljoin(url, href))
                if href == '../' or href == './' or not file_name or href.endswith('/'):
                    continue
                file_path = os.path.join(download_folder, file_name)
                if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                     files_to_download_queue.append({'href': href, 'name': file_name})

    total_files_identified = len(files_to_download_queue)
    print(f"\nIdentified {total_files_identified} new or incomplete files to download.")

    if total_files_identified == 0:
        print("No new or incomplete files to download. All relevant files already exist locally and are complete.")
        pass # Allow zipping existing files

    downloaded_count = 0
    total_downloaded_bytes = 0
    start_time = time.time()
    # Corrected: Use threading.Lock for thread-safe access to total_downloaded_bytes
    total_downloaded_bytes_lock = threading.Lock()

    with tqdm(total=total_files_identified, unit='file', desc="Overall Download Progress", position=0, leave=True) as overall_pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
            future_to_file = {executor.submit(download_single_file, file_info, url, download_folder, headers, overall_pbar, total_downloaded_bytes_lock): file_info for file_info in files_to_download_queue}

            for future in concurrent.futures.as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    success, bytes_downloaded = future.result()
                    if success:
                        downloaded_count += 1
                        # Update total_downloaded_bytes under lock
                        with total_downloaded_bytes_lock:
                            total_downloaded_bytes += bytes_downloaded
                    overall_pbar.update(1)
                except Exception as exc:
                    overall_pbar.write(f'{file_info["name"]} generated an exception: {exc}')

    end_time = time.time()
    total_duration = end_time - start_time
    total_downloaded_mb = total_downloaded_bytes / (1024 * 1024)

    print("-" * 30)
    print(f"Download process complete.")
    print(f"Total files identified for download: {total_files_identified}")
    print(f"New files successfully downloaded this run: {downloaded_count}")
    print(f"Total data downloaded this run: {total_downloaded_mb:.2f} MB")
    print(f"Total time taken for downloads: {total_duration:.2f} seconds")
    print(f"Files saved individually in: {os.path.abspath(download_folder)}")

if __name__ == "__main__":
    directory_url = "https://www.app.shiacast.com/storage/track_media/"
    download_files_from_directory(directory_url)