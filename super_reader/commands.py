import click

@click.command(help="List pipelines")
@click.pass_context
def list_pipeline(ctx: click.Context) -> None:
  names = ctx.obj.pipeline_names()
  for name in names:
    print(name)

@click.command(help="Create a reader")
@click.option('--name', '-n', help="Reader name")
@click.option('--pipeline', '-p', help="Pipeline name")
@click.option('--max-depth', '-md', help="Max Depth")
@click.option('--batch-size', '-bs', help="Batch Size")
@click.pass_context
def create_reader(ctx: click.Context, name: str, pipeline: str, max_depth: int, batch_size: int) -> None:
  ctx.obj.create_reader(name, pipeline, max_depth, batch_size)

@click.command(help="Add web docs")
@click.option('--reader', '-r', help="Reader name")
@click.option('--urls', '-u', help="Bootstrap urls")
@click.pass_context
def add_web_docs(ctx: click.Context, reader: str, urls: str) -> None:
  ctx.obj.add_web_docs(reader, urls.split(","))

@click.command(help="sync web docs")
@click.option('--reader', '-r', help="Reader name")
@click.pass_context
def sync_web_docs(ctx: click.Context, reader: str) -> None:
  ctx.obj.sync_web_docs(reader)