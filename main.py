import cohere
import os
from dotenv import load_dotenv
import hnswlib
import json
import uuid
from typing import List, Dict
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title

load_dotenv()

co = cohere.Client(os.environ["COHERE_API_KEY"])

class Documents:
  def __init__(self, sources: List[Dict[str, str]]):
    self.sources = sources # raw documents
    self.docs = [] # chunked documents
    self.docs_embs = [] # the embeddings of the chunked documents
    self.retrieve_top_k = 10
    self.rerank_top_k = 3
    self.load()
    self.embed()
    self.index()
  
  def load(self) -> None:
    """
    Loads the documents from the sources and chunks the HTML content.
    """
    print("Loading documents...")

    for source in self.sources:
      elements = partition_html(url=source["url"])
      chunks = chunk_by_title(elements)
      for chunk in chunks:
        self.docs.append(
          {
            "title": source["title"],
            "text": str(chunk),
            "url": source["url"],
          }
        )
  
  def embed(self) -> None:
    """
    Embeds the documents using the Cohere API.
    """
    print("Embedding documents...")

    batch_size = 90
    self.docs_len = len(self.docs)

    for i in range(0, self.docs_len, batch_size):
      batch = self.docs[i : min(i + batch_size, self.docs_len)]
      texts = [item["text"] for item in batch]
      docs_embs_batch = co.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type="search_document"
      ).embeddings
      self.docs_embs.extend(docs_embs_batch)
  
  def index(self) -> None:
    """
    Indexes the documents for efficient retrieval.
    """
    print("Indexing documents...")

    self.index = hnswlib.Index(space="ip", dim=1024)
    self.index.init_index(max_elements=self.docs_len, ef_construction=512, M=64)
    self.index.add_items(self.docs_embs, list(range(len(self.docs_embs))))

    print(f"Indexing complete with {self.index.get_current_count()} documents.")

  def retrieve(self, query: str) -> List[Dict[str, str]]:
    docs_retrieved = []
    query_emb = co.embed(texts=[query], model="embed-english-v3.0", input_type="search_query").embeddings
    doc_ids = self.index.knn_query(query_emb, k=self.retrieve_top_k)[0][0]
  
    docs_to_rerank = []
    for doc_id in doc_ids:
      docs_to_rerank.append(self.docs[doc_id]["text"])

    rerank_results = co.rerank(
      query=query,
      documents=docs_to_rerank,
      top_n=self.rerank_top_k,
      model="rerank-english-v2.0",
    )

    doc_ids_reranked = []
    for result in rerank_results:
      doc_ids_reranked.append(doc_ids[result.index])

    for doc_id in doc_ids_reranked:
      docs_retrieved.append(
        {
          "title": self.docs[doc_id]["title"],
          "text": self.docs[doc_id]["text"],
          "url": self.docs[doc_id]["url"],
        }
      )

    return docs_retrieved

class Chatbot:
  def __init__(self, docs: Documents):
    self.docs = docs
    self.conversation_id = str(uuid.uuid4())
  
  def generate_response(self, message: str):
    response = co.chat(message=message, search_queries_only=True)

    if response.search_queries:
      print("Retrieving information...")
      documents = self.retrieve_docs(response)

      response = co.chat(
        message=message,
        documents=documents,
        conversation_id=self.conversation_id,
        stream=True,
      )
      for event in response:
        yield event
    
    else:
      response = co.chat(
        message=message, 
        conversation_id=self.conversation_id, 
        stream=True
      )
      for event in response:
        yield event
  
  def retrieve_docs(self, response) -> List[Dict[str, str]]:
    # Get the query(s)
    queries = []
    for search_query in response.search_queries:
      queries.append(search_query["text"])
    # Retrieve documents for each query
    retrieved_docs = []
    for query in queries:
      retrieved_docs.extend(self.docs.retrieve(query))
    return retrieved_docs

class App:
  def __init__(self, chatbot: Chatbot):
    self.chatbot = chatbot
  
  def run(self):
    while True:
      # Get the user message
      message = input("User: ")

      # Typing "quit" ends the conversation
      if message.lower() == "quit":
        print("Ending chat.")
        break
      else:
        print(f"User: {message}")

        # Get the chatbot response
        response = self.chatbot.generate_response(message)

        # Print the chatbot response
        print("Chatbot:")
        flag = False
        for event in response:
          # Text
          if event.event_type == "text-generation":
            print(event.text, end="")

          # Citations
          if event.event_type == "citation-generation":
            if not flag:
              print("\\n\\nCITATIONS:")
              flag = True
            print(event.citations)

if __name__ == "__main__":
  # Load the sources
  with open("sources.json", "r") as f:
    sources = json.load(f)

  # Create the documents
  docs = Documents(sources)

  # Create the chatbot
  chatbot = Chatbot(docs)

  # Run the app
  app = App(chatbot)
  app.run()