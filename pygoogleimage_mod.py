
"""Drop-in image downloader for the original ECII Stage3 GitHub workflow.

Replaces the old Google HTML parser in pygoogleimage_mod.py with DDGS
(Bing/DuckDuckGo-based image search; not Google Images).

Import from main.py and call:
    pi.download(keywords=combined_keywords, limit=100)

Saves JPEGs into images/<combined_keywords>/ for the existing shutil.move()
step in main.py. Image search results are cached outside images/.

Install dependencies once in the existing virtualenv:
    python -m pip install ddgs Pillow requests
"""

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

MAX_PAGES = 3
PAGE_RESULTS = 100
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MIN_IMAGE_SIZE = 128


def _safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())[:180] or "untitled"


def _search_query(keyword: str) -> str:
    return keyword.replace("_and_", " and ").replace("_", " ") + " photograph"


def _get_candidates(query: str, cache: Path) -> list[dict]:
    if cache.exists():
        with cache.open("r", encoding="utf-8") as fh:
            cached = json.load(fh)
        if cached.get("query") == query:
            print(f"[Images] Reusing {len(cached['results'])} cached search results", flush=True)
            return cached["results"]

    items = []
    seen = set()
    with DDGS(timeout=15) as engine:
        for page in range(1, MAX_PAGES + 1):
            try:
                batch = engine.images(
                    query=query,
                    region="us-en",
                    safesearch="moderate",
                    type_image="photo",
                    max_results=PAGE_RESULTS,
                    page=page,
                    backend="auto",
                )
            except Exception as exc:
                print(f"[Images] Search failed on page {page}: {exc}", flush=True)
                break
            added = 0
            for item in batch or []:
                if not isinstance(item, dict):
                    continue
                url = item.get("image")
                if not isinstance(url, str) or not url.startswith(("https://", "http://")):
                    continue
                if url in seen:
                    continue
                seen.add(url)
                items.append({
                    "image": url,
                    "title": item.get("title", ""),
                    "source_page": item.get("url", ""),
                    "source": item.get("source", ""),
                })
                added += 1
            print(f"[Images] Search page {page}: {added} new image URLs", flush=True)
            if not batch or not added:
                break
            time.sleep(2)  # respect the search provider; do not hammer it

    # Cache search URLs so a failed image download does not require new searches.
    if items:
        cache.parent.mkdir(parents=True, exist_ok=True)
        with cache.open("w", encoding="utf-8") as fh:
            json.dump({"query": query, "results": items}, fh, indent=2)
    return items


def _get_jpeg(session: requests.Session, url: str) -> bytes | None:
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    try:
        with session.get(url, timeout=(6, 12), stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            raw = bytearray()
            for chunk in r.iter_content(chunk_size=65536):
                raw.extend(chunk)
                if len(raw) > MAX_IMAGE_BYTES:
                    return None
        with Image.open(io.BytesIO(raw)) as original:
            if min(original.size) < MIN_IMAGE_SIZE:
                return None
            img = ImageOps.exif_transpose(original).convert("RGB")
            # Keep downloads reasonably small while retaining useful resolution.
            img.thumbnail((2000, 2000))
            out = io.BytesIO()
            img.save(out, format="JPEG", quality=88)
            return out.getvalue()
    except (requests.RequestException, OSError, ValueError, UnidentifiedImageError):
        return None


def download(keywords, limit, directory="", extensions=None):
    """Save up to `limit` usable JPGs per comma-separated keyword query.

    Files: <directory or images>/<keyword>/<keyword>_0001.jpg ...
    Returns: total number of JPGs present after the operation.
    """
    limit = int(limit)
    if limit <= 0:
        raise ValueError("limit must be positive")

    root = Path(directory or "images")
    total = 0
    queries = [k.strip() for k in str(keywords).split(",") if k.strip()]
    if not queries:
        return 0

    with requests.Session() as session:
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; ECIIResearchImageTest/1.0)"})
        for keyword in queries:
            name = _safe_name(keyword)
            target = root / name
            target.mkdir(parents=True, exist_ok=True)
            existing = sorted(target.glob("*.jpg"))
            query = _search_query(keyword)
            print(f"[Images] Query: {query!r}; requested={limit}; existing={len(existing)}", flush=True)

            if len(existing) >= limit:
                total += len(existing)
                print(f"[Images] Already have {len(existing)} images, skipping", flush=True)
                continue

            # Keep cache separate from the class image folder.
            cache = Path(".image_search_cache") / (name + ".json")
            candidates = _get_candidates(query, cache)
            hashes = set()
            for file in existing:
                try:
                    hashes.add(hashlib.sha256(file.read_bytes()).hexdigest())
                except OSError:
                    pass
            count = len(existing)
            next_id = 1
            for item in candidates:
                if count >= limit:
                    break
                content = _get_jpeg(session, item["image"])
                if content is None:
                    continue
                digest = hashlib.sha256(content).hexdigest()
                if digest in hashes:
                    continue
                hashes.add(digest)
                while (target / f"{name}_{next_id:04d}.jpg").exists():
                    next_id += 1
                path = target / f"{name}_{next_id:04d}.jpg"
                path.write_bytes(content)
                count += 1
                next_id += 1
                if count <= 5 or count % 10 == 0 or count == limit:
                    print(f"[Images] Saved {count}/{limit}: {path.name}", flush=True)
                time.sleep(0.15)
            print(f"[Images] Finished {keyword}: {count}/{limit} JPEGs", flush=True)
            if count < 2:
                raise RuntimeError(
                    f"Only {count} images retrieved for {keyword}; "
                    "Stage3 classification requires at least two."
                )
            if count < limit:
                print(
                    f"[Images] Warning: retrieved {count} of {limit} requested images",
                    flush=True,
                )
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
