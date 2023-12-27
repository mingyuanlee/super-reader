import json

def export_to_json(file_name, data):
  with open(file_name, 'w') as file:
    json.dump(data, file, indent=2)

def url_to_file_name(url: str):
  return url.replace('/', '_')

def file_name_to_url(file_name: str):
  return file_name.replace('_', '/')