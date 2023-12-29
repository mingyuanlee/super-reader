from unstructured.partition.html import partition_html
from unstructured.staging.base import convert_to_dict

def process_html(html_text: str):
  elements = partition_html(text=html_text)
  return convert_to_dict(elements)