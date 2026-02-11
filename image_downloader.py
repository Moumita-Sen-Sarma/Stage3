"""
Author: Samatha Ereshi Akkamahadevi
Email: samatha94@ksu.edu
Date: 08/27/2024
Project: Stage3: Parallelized Image Retrieval and Classification
File name: image_downloader.py
Description:
"""

import os
import requests
import shutil
from urllib.parse import urlparse

def sanitize_filename(url):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def download_images(keyword, keyword_folder,folder_name, limit=50, api_key="AIzaSyDqlNYYlxReH51VNgvCFCzfkihxhBU0uEs", cse_id="933de8d069a4a4c8e"):
# def download_images(keyword, base_folder, neuron_index, solution_name, folder_name, limit=5, api_key="AIzaSyDqlNYYlxReH51VNgvCFCzfkihxhBU0uEs", cse_id="933de8d069a4a4c8e"):
    # keyword_folder = create_folder_structure(base_folder, neuron_index, solution_name, folder_name)
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': keyword,
        'cx': cse_id,
        'key': api_key,
        'searchType': 'image',
        'num': 10,  # Adjust if you need more per request, up to 10
        'fileType': 'jpg|png',
    }
    images_downloaded = 0
    start_index = 1
    while images_downloaded < limit:
        params['start'] = start_index
        response = requests.get(search_url, params=params).json()
        if 'items' not in response:
            print("No more images found or there's an error.")
            break
        for item in response['items']:
            image_url = item['link']
            try:
                img_response = requests.get(image_url, stream=True)
                if img_response.status_code == 200:
                    # Naming images sequentially according to the specification
                    # image_name = f"{folder_name} {images_downloaded + 1}.jpg"
                    image_name = folder_name + " " + str(images_downloaded + 1) + ".jpg"
                    file_path = os.path.join(keyword_folder, image_name)
                    with open(file_path, 'wb') as f:
                        img_response.raw.decode_content = True
                        shutil.copyfileobj(img_response.raw, f)
                    images_downloaded += 1
                    if images_downloaded >= limit:
                        break
            except Exception as e:
                # print(f"Failed to download {image_url}. Reason: {e}")
                print("Failed to download " + image_url + ". Reason: " + str(e))
        start_index += 10





