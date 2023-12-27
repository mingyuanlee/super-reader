import click
import sys

from super_reader.app import App
from super_reader.commands import add_web_docs, sync_web_docs


def check_python_version() -> None:
  '''
  Checks that the python version running is sufficient and exits if not.
  '''
  if sys.version_info < (3, 7):
    click.pause('err_python_version')
    sys.exit()


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
  ctx.obj = App()


cli.add_command(add_web_docs)
cli.add_command(sync_web_docs)

if __name__ == '__main__':
  check_python_version()
  cli()