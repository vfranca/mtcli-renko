"""
Comando CLI para geração de gráfico Renko.
"""

import click
from ..controllers.renko_controller import RenkoController
from ..views.renko_view import exibir_renko
import MetaTrader5 as mt5


@click.command()
@click.option("--symbol", "-s", required=True)
@click.option("--brick", "-b", required=True, type=float)
@click.option("--timeframe", "-t", default=mt5.TIMEFRAME_M5)
@click.option("--bars", "-n", default=500)
def renko(symbol, brick, timeframe, bars):
    """
    Gera gráfico Renko em modo texto.
    """

    controller = RenkoController(symbol, brick, timeframe, bars)
    bricks = controller.executar()

    exibir_renko(bricks)
