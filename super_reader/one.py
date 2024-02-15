
import json
import os
from pathlib import Path
from super_reader.ingestion.scraping_service import ScrapingConfig, ScrapingService
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
from dotenv import load_dotenv
from langchain_community.llms import Cohere
from llama_index.core import VectorStoreIndex
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.litellm import LiteLLM

if __name__ == "__main__":
  load_dotenv()

  data_dir = Path('data')
  data_dir.mkdir(exist_ok=True)

  config = ScrapingConfig(max_depth=3, batch_size=20, data_dir=data_dir)
  service = ScrapingService(config)

  # service.add_web_docs(["https://docs.eigenlayer.xyz/eigenlayer"])
  service.sync_web_docs()

  

  documents = []
  for json_file in service.htmls_dir.iterdir():
    with open(json_file, 'r') as file:
      data = json.load(file)
      for obj in data:
        if len(obj['text'].strip()) == 0: continue
        doc = Document(text=obj['text'])
        documents.append(doc)
  
  cohere_api_key = os.environ.get('COHERE_API_KEY')

  llm = LiteLLM("command-nightly")
  embed_model = CohereEmbedding(
      cohere_api_key=cohere_api_key,
      model_name="embed-english-v3.0",
      input_type="search_document",
  )

  index = VectorStoreIndex.from_documents(
    documents=documents, embed_model=embed_model, show_progress=True
  )

  
  cohere_rerank = CohereRerank(api_key=cohere_api_key, top_n=3)

  query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[cohere_rerank],
  )
  
  response = query_engine.query(
    "What is Blob Explorer and how can I use it?"
  )

  print(response)
