from urllib.parse import urljoin, urlparse

base_url = "https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/modules.html"
relative_url = "/../../../api/llama_index.node_parser.MetadataAwareTextSplitter.html"

# Remove the leading slash from the relative URL if it exists
if relative_url.startswith("/"):
  relative_url = relative_url[1:]

absolute_url = urljoin(base_url, relative_url)

print(absolute_url)