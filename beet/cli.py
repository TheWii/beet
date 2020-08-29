__all__ = ["beet", "main"]


from contextlib import contextmanager

import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand, version_option

from . import __version__
from .project import GeneratorError, GeneratorImportError
from .toolchain import Toolchain, ErrorMessage
from .utils import format_exc, format_obj


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="red",
    invoke_without_command=True,
)
@click.pass_context
@click.option(
    "-C",
    "--directory",
    type=click.Path(exists=True, file_okay=False),
    help="The project directory.",
)
@version_option(
    version=__version__,
    prog_name="Beet",
    version_color="yellow",
    prog_name_color="red",
)
def beet(ctx: click.Context, directory: str):
    """The Beet toolchain.

    The `build` command will build the project in the current directory.
    It's also the default command so invoking `beet` without any
    arguments will work exactly as if you used the `build` command
    directly:

        $ beet

    You can use the `init` command to initialize a new project in the
    current directory:

        $ beet init
    """
    ctx.obj = Toolchain(directory)

    if not ctx.invoked_subcommand:
        ctx.invoke(build)


def display_error(message: str, exception: BaseException = None):
    click.secho("Error: " + message, fg="red", bold=True)
    if exception:
        click.echo("\n" + format_exc(exception), nl=False)


@contextmanager
def toolchain_operation(title):
    click.secho(title + "\n", fg="yellow")

    try:
        yield
    except ErrorMessage as exc:
        display_error(" ".join(exc.args))
    except GeneratorImportError as exc:
        generator = format_obj(exc.args[0])
        display_error(f"Couldn't import generator {generator}.", exc.__cause__)
    except GeneratorError as exc:
        generator = format_obj(exc.args[0])
        display_error(f"Generator {generator} raised an exception.", exc.__cause__)
    except Exception as exc:
        display_error("An unhandled exception occurred. This could be a bug.", exc)
    else:
        click.secho("Success.", fg="green", bold=True)


@beet.command(cls=HelpColorsCommand)
@click.pass_context
def build(ctx: click.Context):
    """Build the project in the current directory."""
    with toolchain_operation("Building project..."):
        ctx.obj.build_project()


@beet.command(cls=HelpColorsCommand)
@click.pass_context
def watch(ctx: click.Context):
    """Watch for file changes and rebuild the current project."""
    with toolchain_operation("Watching project..."):
        for change in ctx.obj.watch_project():
            ctx.obj.build_project()


@beet.command(cls=HelpColorsCommand)
@click.pass_context
def init(ctx: click.Context):
    """Initialize a new project in the current directory."""
    with toolchain_operation("Initializing new project..."):
        ctx.obj.init_project()


def main():
    beet(prog_name="beet")
