Three components:
(1) App
(2) Chatbot
(3) Documents


make this a cli?

search-urls: get all urls
bootstrap: get all urls and htmls


Process:
- `super-reader bootstrap --base-url "xxx" --depth 3`
  - search all internal links
  - store the links in `data/urls.json`
  - can remove unused links in the json file
  - can allow adding more docs sources
- `super-reader build-bot --data-folder "data"`
  - build chatbot based on the data in the folder 


Guide: 
- https://txt.cohere.com/rag-chatbot/
- https://unstructured-io.github.io/
- https://docs.llamaindex.ai/en/stable/getting_started/concepts.html


Notes:
1. The data folder:
- webpages
  - urls.json
  - htmls
    - xxx.html
    - ...
- pdfs
  - xxx.pdf
