# from unstructured.partition.html import partition_html
# from unstructured.chunking.title import chunk_by_title

# elements = partition_html(url="https://docs.eigenlayer.xyz/eigenda-guides/eigenda-overview")
# for el in elements:
#   print(el)
# chunks = chunk_by_title(elements)
# print("----------------------")
# for ch in chunks:
#   print(ch)

from super_reader.ingestion.scraping import Scraping

# scraper = Scraper(bootstrap_urls=["https://docs.llamaindex.ai/en/stable/"], max_depth=3)
scraping = Scraping(bootstrap_urls=["https://docs.eigenlayer.xyz/"], max_depth=2)
# scraping.add_web_docs()
# scraping.sync_web_docs()
print(len(list(scraping.htmls_dir.iterdir())))

# asyncio.run(test())