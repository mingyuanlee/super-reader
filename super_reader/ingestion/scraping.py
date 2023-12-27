from collections import deque
import json
from pathlib import Path
import time
import requests
from bs4 import BeautifulSoup
import threading
import aiohttp
import asyncio
from urllib.parse import urljoin

from super_reader.utils.file import export_to_json, file_name_to_url, url_to_file_name

class Scraping:
  def __init__(
    self, 
    bootstrap_urls: list[str], 
    max_depth: int = 2, 
    batch_size: int = 50, 
    base_dir = Path("data"),
  ):
    self.bootstrap_urls = bootstrap_urls
    self.all_urls = []
    self.max_depth = max_depth
    self.batch_size = batch_size
    self.base_dir = base_dir
    self.webpages_dir = base_dir / "webpages"
    self.htmls_dir = self.webpages_dir / "htmls"

    # create data folder structure
    self.htmls_dir.mkdir(parents=True, exist_ok=True)

  # Do BFS to get all internal urls
  # Note that the last depth's urls don't have corresponding html files, need to call sync
  def add_web_docs(self):
    queue = deque(self.bootstrap_urls)
    visited = set()
    depth = 0
    while queue and depth <= self.max_depth:
      size = len(queue)
      # TODO: is result list thread safe?
      result_list = []
      for i in range(0, size, self.batch_size):
        batch_urls = [queue.popleft() for _ in range(min(self.batch_size, len(queue)))]
        self.batch_get_internal_links(i // self.batch_size, batch_urls, result_list)
        time.sleep(0.2)
      internal_links = set()
      for result in result_list:
        internal_links.update(result)
      internal_links = internal_links.difference(visited)
      visited.update(internal_links)
      queue.extend(internal_links)
      self.all_urls.extend(internal_links)
      depth += 1
      print(f"Depth {depth} done: {len(internal_links)} urls added.")
      print("-------------------------------")
    self.all_urls = sorted(self.all_urls)
    export_to_json(self.webpages_dir / "urls.json", self.all_urls)

  def sync_web_docs(self):
    # TODO: here we assume urls.json exists
    with open(self.webpages_dir / 'urls.json', 'r') as file:
      urls = json.load(file)
    missing_html_urls = []
    url_set = set(urls)
    # Download if no matching html file
    for url in url_set:
      html_file = self.htmls_dir / f"{url_to_file_name(url)}.html"
      if not html_file.exists():
        missing_html_urls.append(url)
    # Delete if no matching url in the urls.json
    delete_count = 0
    for html_file in self.htmls_dir.iterdir():
      if html_file.is_file():
        url_from_file = file_name_to_url(html_file.stem)
        if url_from_file not in url_set:
          html_file.unlink()
          delete_count += 1
    # Batch download
    for i in range(0, len(missing_html_urls), self.batch_size):
      batch_urls = missing_html_urls[i : min(i + self.batch_size, len(missing_html_urls))]
      url_to_text = asyncio.run(self.batch_fetch_url(batch_urls))
      # save as html files
      self.save_as_html_files(url_to_text)
    print(f"Finish syncing. Downloaded {len(missing_html_urls)} html files. Deleted {delete_count} unused files.")

  async def fetch_url(self, session, url: str):
    try:
      async with session.get(url) as response:
        return url, await response.text()
    except Exception as e:
      print(f"Error fetching {url}: {e}")
      return None
  
  async def batch_fetch_url(self, urls: list[str]):
    async with aiohttp.ClientSession() as session:
      tasks = [self.fetch_url(session, url) for url in urls]
      results = await asyncio.gather(*tasks)
      return dict(results)
  
  def merge_url(self, base_url, relative_url):
    absolute_url = urljoin(base_url, relative_url)
    return absolute_url

  def parse_html(self, html: str, results: list[str], base_url: str):
    try:
      soup = BeautifulSoup(html, "lxml")
      a_tags = set(soup.html.body.findAll("a"))
      internal_links = []
      for a_tag in a_tags:
        link = a_tag.get("href")
        if link.startswith("http") or link.startswith("#"):
          continue
        internal_links.append(self.merge_url(base_url, link))
      results.extend(internal_links)
    except Exception as e:
      print(f"An error occurred: {e}")

  def batch_get_internal_links(self, batch_id: int, urls: list[str], result_list: list[set[str]]) -> None:
    print(f"Batch {batch_id} started...")
    start = time.time()
    url_to_text = asyncio.run(self.batch_fetch_url(urls))
    # TODO: is results thread safe?
    results = []
    threads = []
    # save as html files
    self.save_as_html_files(url_to_text)
    # concurrently parse html
    for url, text in url_to_text.items():
      thread = threading.Thread(target=self.parse_html, args=(text, results, url))
      threads.append(thread)
      thread.start()
    for thread in threads:
      thread.join()
    results = set(results)
    result_list.append(results)
    end = time.time()
    print(f"Batch done: {end - start:.2f}s", f"{len(results)} urls found.")
        
  def save_as_html_files(self, url_to_text: dict[str, str]):
    for url, text in url_to_text.items():
      file_name = f"{url_to_file_name(url)}.html"
      with open(self.htmls_dir / file_name, "w") as file:
        file.write(text)