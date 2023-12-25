from collections import deque
import requests
from bs4 import BeautifulSoup

class Scraper:
  def __init__(self, bootstrap_urls: list[str], max_depth: int = 3):
    self.bootstrap_urls = bootstrap_urls
    self.all_urls = []
    self.max_depth = max_depth

  # Do BFS to get all internal urls
  def bootstrap(self):
    queue = deque(self.bootstrap_urls)
    visited = set()
    depth = 0
    while queue and depth <= self.max_depth:
      size = len(queue)
      for i in range(size):
        print(i)
        url = queue.popleft()
        internal_links = self.get_internal_links(url)
        for link in internal_links:
          if link not in visited:
            visited.add(link)
            queue.append(link)
            self.all_urls.append(link)
      depth += 1
      print(f"Depth {depth} done: {queue}")
    print(self.all_urls)

  def get_internal_links(self, url: str) -> list[str]:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    a_tags = set(soup.html.body.findAll("a"))
    internal_links = []
    for a_tag in a_tags:
      link = a_tag.get("href")
      if link.startswith("http") or link.startswith("#"):
        continue
      internal_links.append(url + "/" + link)
    return internal_links
  
  def test(self):
    # print(len(self.get_internal_links("https://docs.llamaindex.ai/en/stable")))
    self.bootstrap()


if __name__ == "__main__":
  scraper = Scraper(bootstrap_urls=["https://docs.llamaindex.ai/en/stable/"], max_depth=3)
  scraper.test()