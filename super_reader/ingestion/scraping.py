from collections import deque
import json
import time
import requests
from bs4 import BeautifulSoup
import threading
import aiohttp
import asyncio
from urllib.parse import urljoin

class Scraping:
  def __init__(self, bootstrap_urls: list[str], max_depth: int = 2, batch_size: int = 50):
    self.bootstrap_urls = bootstrap_urls
    self.all_urls = []
    self.max_depth = max_depth
    self.batch_size = 50

  # Do BFS to get all internal urls
  def bootstrap(self):
    queue = deque(self.bootstrap_urls)
    visited = set()
    depth = 0
    while queue and depth <= self.max_depth:
      size = len(queue)
      # TODO: is result list thread safe?
      result_list = []
      for i in range(0, size, self.batch_size):
        print(f"Batch {i} to {i + self.batch_size}, total {size}...")
        batch_urls = [queue.popleft() for _ in range(min(self.batch_size, len(queue)))]
        self.batch_get_internal_links(batch_urls, result_list)
        time.sleep(0.2)
      internal_links = set()
      for result in result_list:
        internal_links.update(result)
      internal_links = internal_links.difference(visited)
      visited.update(internal_links)
      queue.extend(internal_links)
      self.all_urls.extend(internal_links)
      depth += 1
      print(f"Depth {depth} done: {len(internal_links)}")
    print(self.all_urls)

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

  def batch_get_internal_links(self, urls: list[str], result_list: list[set[str]]) -> None:
    start = time.time()
    url_to_text = asyncio.run(self.batch_fetch_url(urls))
    # TODO: is results thread safe?
    results = []
    threads = []
    for url, text in url_to_text.items():
      thread = threading.Thread(target=self.parse_html, args=(text, results, url))
      threads.append(thread)
      thread.start()
    for thread in threads:
      thread.join()
    results = set(results)
    result_list.append(results)
    end = time.time()
    print(f"batch done: {end - start}s", list(results)[:50], len(results))

  def export_to_json(self, file_name):
    with open(file_name, 'w') as file:
      json.dump(self.all_urls, file, indent=2)

  def run(self):
    while True:
      cmd = input("Enter a command: ")
      if cmd == "quit":
        break
      elif cmd == "bootstrap":
        self.bootstrap()
      elif cmd == "export":
        self.export_to_json("data/urls.json")
      elif cmd == "count":
        print(len(self.all_urls))
      elif cmd == "sort":
        with open("data/urls.json", 'r') as file:
          data = json.load(file)
          sorted_data = sorted(data)

        with open("data/urls.json", 'w') as file:
          json.dump(sorted_data, file, indent=2)
        

async def test():
  scraper = Scraper(bootstrap_urls=["https://docs.eigenlayer.xyz/"], max_depth=2)
  res = await scraper.batch_fetch_url(["https://docs.eigenlayer.xyz/avs-guides/avs-developer-guide"])
  html = res["https://docs.eigenlayer.xyz/avs-guides/avs-developer-guide"]
  soup = BeautifulSoup(html, "lxml")
  a_tags = set(soup.html.body.findAll("a"))
  for tag in a_tags:
    print(tag.get("href"))
  results = []
  scraper.parse_html(html, results, "https://docs.eigenlayer.xyz/avs-guides/avs-developer-guide")
  print("------------------")
  for a in results:
    print(a)

if __name__ == "__main__":
  # scraper = Scraper(bootstrap_urls=["https://docs.llamaindex.ai/en/stable/"], max_depth=3)
  scraper = Scraper(bootstrap_urls=["https://docs.eigenlayer.xyz/"], max_depth=2)
  scraper.run()

  # asyncio.run(test())