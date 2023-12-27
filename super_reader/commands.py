import click

@click.command(help="Add web docs")
@click.option('--bootstrap-urls', '-urls', help="Bootstrap urls")
@click.pass_context
def add_web_docs(ctx: click.Context, bootstrap_urls: str) -> None:
  urls = bootstrap_urls.split(",")
  ctx.obj.scraping.add_web_docs(urls)

@click.command(help="sync web docs")
@click.pass_context
def sync_web_docs(ctx: click.Context) -> None:
  ctx.obj.scraping.sync_web_docs()