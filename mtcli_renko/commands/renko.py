"""
Comando CLI para geração de gráfico Renko.
"""

import click

from ..controllers.renko_controller import RenkoController
from ..views.renko_view import exibir_renko
from ..domain.timeframe import Timeframe
from mtcli.logger import setup_logger
from ..conf import SYMBOL, BRICK, PERIOD, BARS

log = setup_logger(__name__)


@click.command()
@click.version_option(package_name="mtcli-renko")
@click.option("--symbol", "-s", default=SYMBOL, show_default=True)
@click.option("--brick", "-b", default=BRICK, show_default=True, type=float)
@click.option("--timeframe", "-t", default=PERIOD, show_default=True)
@click.option("--bars", "-n", default=BARS, show_default=True, type=int)
@click.option("--numerar/--no-numerar", default=False, show_default=True)
@click.option(
    "--modo",
    type=click.Choice(["simples", "classico"], case_sensitive=False),
    default="simples",
    show_default=True,
)
@click.option(
    "--ancorar-abertura",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option(
    "--data-mode",
    type=click.Choice(["candle", "tick"], case_sensitive=False),
    default="candle",
    show_default=True,
)
@click.option(
    "--max-ticks",
    default=3000,
    show_default=True,
    type=int,
    help="Limite máximo de ticks processados no modo tick.",
)
def renko(
    symbol,
    brick,
    timeframe,
    bars,
    numerar,
    modo,
    ancorar_abertura,
    data_mode,
    max_ticks,
):

    try:
        tf_enum = Timeframe.from_string(timeframe)
    except ValueError as e:
        raise click.BadParameter(str(e))

    controller = RenkoController(
        symbol,
        brick,
        tf_enum.mt5_const,
        bars,
        modo,
        ancorar_abertura,
        data_mode,
        max_ticks,
    )

    bricks = controller.executar()
    exibir_renko(bricks, numerar=numerar)
