import json
from pathlib import Path
from typing import List
from llama_index import Document
from super_reader.ingestion.scraping_service import ScrapingConfig, ScrapingService
from super_reader.pipeline.pipeline import Pipeline
from super_reader.reader.repo import Repo
from unstructured.chunking.title import chunk_by_title
from unstructured.staging.base import dict_to_elements, convert_to_dict
from llama_index import VectorStoreIndex
from llama_index.ingestion import IngestionPipeline

class Reader:
  def __init__(self, name: str, pipeline: Pipeline, config: ScrapingConfig, base_dir: Path):
    self._name = name
    self._pipeline = pipeline
    self._reader_dir = base_dir / name
    self._repo = Repo(name, self._reader_dir)
    self._index = None
    self._scraping_config = config
    self._scraping_service = ScrapingService(config)

  def get_scraping_config(self) -> ScrapingConfig:
    return self._scraping_config

  def add_web_docs(self, urls: List[str]):
    self._scraping_service.add_web_docs(urls, self._repo.get_webpages_dir())
  
  def sync_web_docs(self):
    self._scraping_service.sync_web_docs(self._repo.get_htmls_dir())

  def build_index(self):
    docs = self.load_documents()
    pipeline = IngestionPipeline(transformations=self._pipeline)
    nodes = pipeline.run(documents=docs)
    self._index = VectorStoreIndex(nodes)

  def load_documents(self):
    documents = []
    for html_file in self.htmls_dir.glob("*.json"):
      with open(html_file, 'r') as file:
        elements = json.loads(file.read())
      chunks = chunk_by_title(dict_to_elements(elements))
      chunks = convert_to_dict(chunks)
      for chunk in chunks:
        documents.append(Document(text=chunk["text"]))
    return documents

  # def get_docs(self):
  #   return self.documents

  # def add_index(self, index_name, index):
  #   self._index_map[index_name] = index
  
  def create_chat_engine(self, index_name):
    index = self._index_map[index_name]
    chat_engine = index.as_chat_engine()
    streaming_response = chat_engine.stream_chat("Tell me a joke.")
    for token in streaming_response.response_gen:
      print(token, end="")
  