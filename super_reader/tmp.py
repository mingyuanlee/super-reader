from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title

elements = partition_html(url="https://docs.eigenlayer.xyz/eigenda-guides/eigenda-overview")
for el in elements:
  print(el)
chunks = chunk_by_title(elements)
print("----------------------")
for ch in chunks:
  print(ch)