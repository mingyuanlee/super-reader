
### Set up

1. Create virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. 


### Commands

- `super-reader add-pipeline --name <pipeline-name>`: not implemented yet
- `super-reader list-pipeline`
- `super-reader create-reader --name <reader-name> --pipeline <pipeline-name> --max-depth <depth> --batch-size <size>`
- `super-reader add-web-docs --reader <reader-name> --urls <url>`
- `super-reader sync-web-docs --reader <reader-name>`
- `super-reader list-reader`
- `super-reader build-index --reader <reader-name>`
- `super-reader start-chat --reader <reader-name>`

### Abstraction

- Repo: A set of documents
- Reader: Each reader has its own topic, repo and an index from these documents. 
- App: Each app contains a list of readers, a list of pipelines and a list of repos.
- The design is not good for scaling, but let's use this first


### Legacy below:


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

To run:
```
python3 -m super_reader.cli add-web-docs -urls https://docs.eigenlayer.xyz/
```