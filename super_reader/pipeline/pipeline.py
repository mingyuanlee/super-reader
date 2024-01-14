from llama_index import VectorStoreIndex
from llama_index.embeddings import OpenAIEmbedding
from llama_index.text_splitter import SentenceSplitter
from llama_index.extractors import TitleExtractor

class Pipeline:
    def __init__(self, name: str) -> None:
        self._name = name
        self._transformations = [
            SentenceSplitter(chunk_size=50, chunk_overlap=0),
            TitleExtractor(),
            OpenAIEmbedding(),
        ]
    
    def get_transformations(self):
        return self._transformations
