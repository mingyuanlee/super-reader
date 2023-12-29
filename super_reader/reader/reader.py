import json
from llama_index import Document
from super_reader.ingestion.scraping import Scraping
from unstructured.chunking.title import chunk_by_title
from unstructured.staging.base import dict_to_elements, convert_to_dict

class ReaderConfig:
  def __init__(self, max_depth, batch_size, base_dir):
    self.max_depth = max_depth
    self.batch_size = batch_size 
    self.base_dir = base_dir

class Reader:
  def __init__(self, name: str, config: ReaderConfig):
    self._name = name
    self.base_dir = config.base_dir
    self.webpages_dir = self.base_dir / "webpages"
    self.htmls_dir = self.webpages_dir / "htmls"
    self.Scraping = Scraping(config.max_depth, config.batch_size, self.base_dir)
    self.load_documents()

    self._index_map = {}
  
  def load_documents(self):
    self.documents = []
    for html_file in self.htmls_dir.glob("*.json"):
      with open(html_file, 'r') as file:
        elements = json.loads(file.read())
      chunks = chunk_by_title(dict_to_elements(elements))
      chunks = convert_to_dict(chunks)
      for chunk in chunks:
        self.documents.append(Document(text=chunk["text"]))

  def get_docs(self):
    return self.documents

  def add_index(self, index_name, index):
    self._index_map[index_name] = index
  
  def create_chat_engine(self, index_name):
    index = self._index_map[index_name]
    chat_engine = index.as_chat_engine()
    streaming_response = chat_engine.stream_chat("Tell me a joke.")
    for token in streaming_response.response_gen:
      print(token, end="")
  