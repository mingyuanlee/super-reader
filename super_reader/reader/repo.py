from pathlib import Path

class Repo:
  def __init__(self, name: str, base_dir: Path):
    self._repo_dir = base_dir / name
    self._webpages_dir = self._repo_dir / "webpages"
    self._htmls_dir = self._webpages_dir / "htmls"

    # create data folder structure
    self.htmls_dir.mkdir(parents=True, exist_ok=True)
  
  def get_repo_dir(self):
    return self._repo_dir
  
  def get_webpages_dir(self):
    return self._webpages_dir
  
  def get_htmls_dir(self):
    return self._htmls_dir