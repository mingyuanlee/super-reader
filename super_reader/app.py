import os
from pathlib import Path
from llama_index import VectorStoreIndex
from llama_index.embeddings import OpenAIEmbedding
from llama_index.text_splitter import SentenceSplitter
from llama_index.extractors import TitleExtractor
from llama_index.ingestion import IngestionPipeline, IngestionCache
from llama_index.vector_stores import PineconeVectorStore

import pinecone

import dotenv

from super_reader.reader.reader import Reader, ReaderConfig


dotenv.load_dotenv()

class App:
  def __init__(self) -> None:
    self._readers = {}
    self._pipelines = {}

    self.load_readers()
    self.load_pipelines()
    # self.load_vector_store_configs()
    self.curr_reader = self._readers["EigenLayer"]
  
  def load_readers(self) -> None:
    url = "data"
    reader_config = ReaderConfig(3, 50, Path(url))
    self._readers["EigenLayer"] = Reader("EigenLayer", reader_config)

  # def load_vector_store_configs(self) -> None:
  #   self._vector_store_configs = {}
  #   # model parameters like dimensions can be found here: https://docs.cohere.com/docs/models
  #   self._vector_store_configs["pinecone"] = {
  #     "name": "pinecone",
  #     "provider": "pinecone",
  #     "model": "embed-english-v3.0",
  #     "dimensions": 1024,
  #     "max_tokens": 512
  #   }

  #   api_key = os.environ["PINECONE_API_KEY"]
  #   pinecone.init(api_key=api_key, environment="eu-west1-gcp")
  
  def load_pipelines(self):
    name = "test-pipeline"
    transformations = [
      SentenceSplitter(chunk_size=50, chunk_overlap=0),
      TitleExtractor(),
      OpenAIEmbedding(),
    ]
    self._pipelines[name] = transformations
  
  def create_index(self, pipeline_name: str) -> None:
    # TODO: check reader and vector_stores exist
    transformations = self._pipelines[pipeline_name]
    # vector_store_config = self._vector_store_configs[vector_store_name]
    # vector_store = PineconeVectorStore(pinecone_index=pinecone_index)    
    pipeline = IngestionPipeline(transformations=transformations)
    nodes = pipeline.run(documents=self.curr_reader.get_docs())
    index_name = f"{pipeline_name}"
    index = VectorStoreIndex(nodes)
    self.curr_reader.add_index(index_name, index)
  
  def create_chat_engine(self, index_name):
    self.curr_reader.create_chat_engine(index_name)


if __name__ == "__main__":
  app = App()
  app.create_index("test-pipeline")
  app.create_chat_engine("test-pipeline")