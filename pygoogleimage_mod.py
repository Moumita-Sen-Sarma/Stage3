from __future__ import annotations

import hashlib
import io
import json
import re
import time
from pathlib import Path
from urllib.parse import urlsplit

import requests
from PIL import Image, ImageOps, UnidentifiedImageError
from ddgs import DDGS

MAX_IMAGE_BYTES = 12 * 1024 * 1024
MIN_IMAGE_SIZE = 128
MAX_PAGES = 5
PAGE_RESULTS = 100


def _safe_name(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())[:180] or "untitled"


def _get_jpeg(session, url):
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    try:
        with session.get(url, timeout=(6, 12), stream=True, allow_redirects=True) as response:
            response.raise_for_status()
            raw = bytearray()
            for chunk in response.iter_content(chunk_size=65536):
                raw.extend(chunk)
                if len(raw) > MAX_IMAGE_BYTES:
                    return None
        with Image.open(io.BytesIO(raw)) as original:
            if min(original.size) < MIN_IMAGE_SIZE:
                return None
            img = ImageOps.exif_transpose(original).convert("RGB")
            img.thumbnail((2000, 2000))
            out = io.BytesIO()
            img.save(out, format="JPEG", quality=88)
            return out.getvalue()
    except (requests.RequestException, OSError, ValueError, UnidentifiedImageError):
        return None


def _verified_jpgs(folder):
    valid = []
    for path in sorted(folder.glob("*.jpg")):
        try:
            with Image.open(path) as image:
                image.verify()
            valid.append(path)
        except (OSError, ValueError, UnidentifiedImageError):
            print(f"[Images] Invalid existing file ignored: {path}", flush=True)
    return valid


def download(keywords, limit=100, directory="", extensions=None):
    """Top up one query to EXACTLY `limit` decodable JPG files.

    Downloads directly to directory/<safe-keyword>/. Existing valid JPGs
    are preserved. On failure, raises RuntimeError rather than quietly
    returning an incomplete image set.
    """
    limit = int(limit)
    if limit <= 0:
        raise ValueError("limit must be positive")

    root = Path(directory or "images")
    queries = [q.strip() for q in str(keywords).split(",") if q.strip()]
    if not queries:
        raise ValueError("No search query supplied")

    total = 0
    with requests.Session() as session:
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; ECIIResearchImageTest/1.0)"})
        for keyword in queries:
            name = _safe_name(keyword)
            target = root / name
            target.mkdir(parents=True, exist_ok=True)
            existing = _verified_jpgs(target)
            count = len(existing)
            if count > limit:
                raise RuntimeError(f"{target} contains {count} valid JPGs; won't delete any to reach {limit}")
            if count == limit:
                print(f"[Images] Complete: {target}: {count}/{limit}", flush=True)
                total += count
                continue

            hashes = {hashlib.sha256(p.read_bytes()).hexdigest() for p in existing}
            cache = Path(".image_search_cache") / (name + ".json")
            seen_urls = set()
            # Seed from an existing cache if available. Search providers may be
            # queried again with variations because old results are not enough.
            cached = []
            if cache.exists():
                try:
                    cached = json.loads(cache.read_text()).get("results", [])
                except (OSError, ValueError, TypeError):
                    pass

            base = keyword.replace("_and_", " and ").replace("_", " ")
            queries_to_try = [base + " photograph", base + " photo", base + " images", base]
            next_id = 1

            def consume(items):
                nonlocal count, next_id
                for item in items or []:
                    if count >= limit:
                        break
                    url = item.get("image") if isinstance(item, dict) else None
                    if not isinstance(url, str) or not url.startswith(("http://", "https://")) or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    jpeg = _get_jpeg(session, url)
                    if jpeg is None:
                        continue
                    digest = hashlib.sha256(jpeg).hexdigest()
                    if digest in hashes:
                        continue
                    while (target / f"{name}_{next_id:04d}.jpg").exists():
                        next_id += 1
                    path = target / f"{name}_{next_id:04d}.jpg"
                    path.write_bytes(jpeg)
                    hashes.add(digest)
                    count += 1
                    next_id += 1
                    if count % 10 == 0 or count == limit:
                        print(f"[Images] {target}: {count}/{limit}", flush=True)
                    time.sleep(0.15)

            consume(cached)
            if count < limit:
                with DDGS(timeout=15) as engine:
                    for query in queries_to_try:
                        if count >= limit:
                            break
                        for page in range(1, MAX_PAGES + 1):
                            if count >= limit:
                                break
                            try:
                                batch = engine.images(
                                    query=query, region="us-en", safesearch="moderate",
                                    type_image="photo", max_results=PAGE_RESULTS,
                                    page=page, backend="auto",
                                )
                            except Exception as exc:
                                print(f"[Images] Search error {query!r} page {page}: {exc}", flush=True)
                                break
                            if not batch:
                                break
                            consume(batch)
                            time.sleep(2)

            # Fresh count after new files are written.
            count = len(_verified_jpgs(target))
            if count != limit:
                raise RuntimeError(f"Only {count}/{limit} valid JPGs in {target}. Search exhausted; retry later or broaden query.")
            total += count
    return total



# ------------------old module--------------
# import os
# import time
# import requests
# import urllib
# import magic
# import progressbar
# from urllib.parse import quote


# def __init__():
#     pass


# def _create_directories(_directory, _name):
#     """
#     create directory to save images
#     :param _directory:
#     :param _name:
#     :return:
#     """
#     name = _name.replace(" ", "_")
#     try:
#         if not os.path.exists(_directory):
#             os.makedirs(_directory)
#             time.sleep(0.2)
#             path = name
#             sub_directory = os.path.join(_directory, path)
#             if not os.path.exists(sub_directory):
#                 os.makedirs(sub_directory)
#         else:
#             path = name
#             sub_directory = os.path.join(_directory, path)
#             if not os.path.exists(sub_directory):
#                 os.makedirs(sub_directory)

#     except OSError as e:
#         if e.errno != 17:
#             raise
#         pass
#     return


# def _download_page(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#     }
#     r = requests.get(url, headers=headers, timeout=20)
#     r.raise_for_status()
#     return r.text


# def download(keywords, limit, directory='', extensions={'.jpg', '.png', '.ico', '.gif', '.jpeg'}):
#     """
#     download images from google images
#     :param keywords:
#     :param limit:
#     :param directory:
#     :param extensions:
#     :return:
#     """
#     keyword_to_search = [str(item).strip() for item in keywords.split(',')]
#     if directory != '':
#         main_directory = directory
#     else:
#         main_directory = "images/"

#     i = 0

#     things = len(keyword_to_search) * limit

#     bar = progressbar.ProgressBar(maxval=things, \
#                                   widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

#     bar.start()

#     while i < len(keyword_to_search):
#         _create_directories(main_directory, keyword_to_search[i])
#         url = 'https://www.google.com/search?q=' + quote(
#             keyword_to_search[i].encode(
#                 'utf-8')) + '&biw=1536&bih=674&tbm=isch&sxsrf=ACYBGNSXXpS6YmAKUiLKKBs6xWb4uUY5gA:1581168823770&source=lnms&sa=X&ved=0ahUKEwioj8jwiMLnAhW9AhAIHbXTBMMQ_AUI3QUoAQ'
#         raw_html = _download_page(url)

#         end_object = -1;
#         google_image_seen = False;
#         j = 0
#         while j < limit:
#             while (True):
#                 try:
#                     new_line = raw_html.find('"https://', end_object + 1)
#                     end_object = raw_html.find('"', new_line + 1)

#                     buffor = raw_html.find('\\', new_line + 1, end_object)
#                     if buffor != -1:
#                         object_raw = (raw_html[new_line + 1:buffor])
#                     else:
#                         object_raw = (raw_html[new_line + 1:end_object])

#                     if any(extension in object_raw for extension in extensions):
#                         break

#                 except Exception as e:
#                     break
#             path = main_directory + keyword_to_search[i].replace(" ", "_")

#             try:
#                 r = requests.get(object_raw, allow_redirects=True, timeout=1)
#                 if ('html' not in str(r.content)):
#                     mime = magic.Magic(mime=True)
#                     file_type = mime.from_buffer(r.content)
#                     file_extension = f'.{file_type.split("/")[1]}'
#                     if file_extension not in extensions:
#                         raise ValueError()
#                     if file_extension == '.png' and not google_image_seen:
#                         google_image_seen = True
#                         raise ValueError()
#                     file_name = str(keyword_to_search[i]) + "_" + str(j + 1) + file_extension
#                     with open(os.path.join(path, file_name), 'wb') as file:
#                         file.write(r.content)
#                     bar.update(bar.currval + 1)
#                 else:
#                     j -= 1
#             except Exception as e:
#                 j -= 1
#             j += 1

#         i += 1
#     bar.finish()
