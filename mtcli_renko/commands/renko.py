"""
Comando CLI para geração de gráfico Renko.
"""

import click

from ..controllers.renko_controller import RenkoController
from ..views.renko_view import exibir_renko
from ..domain.timeframe import Timeframe
from mtcli.logger import setup_logger
from ..conf import (
    SYMBOL,
    BRICK,
    PERIOD,
    BARS
)

log = setup_logger(__name__)


@click.command()
@click.version_option(package_name="mtcli-renko")
@click.option(
    "--symbol",
    "-s",
    default=SYMBOL,
    show_default=True,
    help="Ativo (ex: WINJ26)",
)
@click.option(
    "--brick",
    "-b",
    default=BRICK,
    show_default=True,
    type=float,
    help="Tamanho do brick em pontos",
)
@click.option(
    "--timeframe",
    "-t",
    default=PERIOD,
    show_default=True,
    help=f"Timeframe ({', '.join(Timeframe.valid_labels())})",
)
@click.option(
    "--bars",
    "-n",
    default=BARS,
    show_default=True,
    help="Quantidade de candles para cálculo",
)
@click.option(
    "--numerar/--no-numerar",
    default=False,
    show_default=True,
    help="Exibir numeração das linhas",
)
def renko(symbol, brick, timeframe, bars, numerar):
    """
    Gera gráfico Renko em modo texto (screen reader friendly).
    """

    try:
        tf_enum = Timeframe.from_string(timeframe)
    except ValueError as e:
        raise click.BadParameter(str(e))

    log.info(
        f"[Renko CLI] symbol={symbol} | brick={brick} | "
        f"timeframe={tf_enum.label} | bars={bars} | "
        f"numerar={numerar}"
    )

    controller = RenkoController(
        symbol,
        brick,
        tf_enum.mt5_const,
        bars,
    )

    bricks = controller.executar()
    exibir_renko(bricks, numerar=numerar)
