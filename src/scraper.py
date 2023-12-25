from collections import deque
import time
import requests
from bs4 import BeautifulSoup
import threading
import aiohttp
import asyncio
from urllib.parse import urljoin

class Scraper:
  def __init__(self, bootstrap_urls: list[str], max_depth: int = 3):
    self.bootstrap_urls = bootstrap_urls
    self.all_urls = []
    self.max_depth = max_depth
    self.batch_size = 30

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
        print("batch", i, "start")
        threads = []
        batch_urls = [queue.popleft() for _ in range(min(self.batch_size, len(queue)))]
        for url in batch_urls:
          thread = threading.Thread(target=self.get_internal_links, args=(url, result_list))
          threads.append(thread)
          thread.start()
        j = 0
        for thread in threads:
          j += 1
          thread.join()
        time.sleep(0.2)
        print("batch", i, "end: ", len(result_list))
      
      internal_links = set()
      for result in result_list:
        internal_links.update(result)
      internal_links = internal_links.difference(visited)
      queue.extend(internal_links)
      self.all_urls.extend(internal_links)
      depth += 1
      print(f"Depth {depth} done: {len(queue)}")
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
    if relative_url.startswith("/"):
      relative_url = relative_url[1:]
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

  def batch_get_internal_links(self, base_url: str, urls: list[str], result_list: list[set[str]]) -> None:
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
    



    
  def get_internal_links(self, url: str, result_list: list[list[str]]) -> None:
    try:
      # print("internal link 1")
      html = requests.get(url, timeout=10).text
      # print("internal link 2")
      soup = BeautifulSoup(html, "lxml")
      # print("internal link 3")
      a_tags = set(soup.html.body.findAll("a"))
      # print("internal link:", len(a_tags))
      internal_links = []
      for a_tag in a_tags:
        # print("internal link:", a_tag)
        link = a_tag.get("href")
        if link.startswith("http") or link.startswith("#"):
          continue
        internal_links.append(url + "/" + link)
      result_list.append(internal_links)
    except Exception as e:
      print(f"An error occurred: {e}")
  
  def test(self):
    res = []
    self.get_internal_links("https://docs.llamaindex.ai/en/stable/", res)
    print(res[0][:30])
    self.batch_get_internal_links("https://docs.llamaindex.ai/en/stable/", res[0][:30], [])


if __name__ == "__main__":
  scraper = Scraper(bootstrap_urls=["https://docs.llamaindex.ai/en/stable/"], max_depth=3)
  scraper.test()