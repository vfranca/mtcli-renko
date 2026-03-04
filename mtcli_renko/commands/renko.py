"""
Comando CLI para geração de gráfico Renko.
"""

import click

from ..controllers.renko_controller import RenkoController
from ..views.renko_view import exibir_renko
from mtcli.domain.timeframe import Timeframe
from mtcli.logger import setup_logger
from ..conf import (
    SYMBOL,
    BRICK,
    PERIOD,
    BARS,
    DATA_MODE,
    MAX_TICKS,
    TICK_STYLE,
    MODO,
    LIMIT_BRICKS
)
from ..utils.renko_stats import exibir_stats
from ..utils.renko_stats import exibir_levels
from ..utils.renko_stats import exibir_trend


log = setup_logger(__name__)


@click.command("renko")
@click.version_option(package_name="mtcli-renko")
@click.option("--symbol", "-s", default=SYMBOL, show_default=True)
@click.option("--brick", "-b", default=BRICK, show_default=True, type=float)
@click.option("--timeframe", "-t", default=PERIOD, show_default=True)
@click.option("--bars", "-n", default=BARS, show_default=True, type=int)
@click.option("--numerar/--no-numerar", default=False, show_default=True)
@click.option(
    "--modo", "-m",
    type=click.Choice(["simples", "classico"], case_sensitive=False),
    default=MODO,
    show_default=True,
    help="Modo de calculo dos blocos"
)
@click.option("--ancorar-abertura", "-a", is_flag=True, show_default=True, help="Ancora na abertura do pregão")
@click.option(
    "--data-mode", "-dm",
    type=click.Choice(["candle", "tick"]),
    default=DATA_MODE,
    show_default=True,
    help="Dados baseados em candles ou ticks"
)
@click.option("--max-ticks", "-mt", default=MAX_TICKS, type=int, show_default=True, help="Maximo de ticks usados no renko baseado em ticks")
@click.option(
    "--tick-style", "-ts",
    type=click.Choice(["estrutural", "hibrido", "agressivo"]),
    default=TICK_STYLE,
    show_default=True,
    help="Estilo de calculo dos blocos baseado em ticks"
)
@click.option("--limit-bricks", "-lb", type=int, default=LIMIT_BRICKS, show_default=True, help="Limite de blocos")
@click.option("--price-min", "-mn", type=float, default=None, show_default=True, help="Preço mínimo para filtrar blocos")
@click.option("--price-max", "-mx", type=float, default=None, show_default=True, help="Preço máximo para filtrar blocos")
@click.option("--reverse", "-r", is_flag=True, show_default=True, help="Reverte a órdem dos blocos")
@click.option("--stats", "-st", is_flag=True, help="Exibe estatísticas do Renko")
@click.option("--levels", "-l", is_flag=True, help="Exibe níveis importantes do Renko")
@click.option("--trend", "-tr", is_flag=True, help="Exibe direção atual do Renko")
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
    tick_style,
    limit_bricks,
    price_min,
    price_max,
    reverse,
    stats,
    levels,
    trend,
):
    """
    Gera gráfico Renko no terminal.
    """

    try:
        tf_enum = Timeframe.from_string(timeframe)
    except ValueError as e:
        raise click.BadParameter(str(e))

    controller = RenkoController(
        symbol=symbol,
        brick_size=brick,
        timeframe=tf_enum.mt5_const,
        quantidade=bars,
        modo=modo,
        ancorar_abertura=ancorar_abertura,
        data_mode=data_mode,
        max_ticks=max_ticks,
        tick_style=tick_style,
        price_min=price_min,
        price_max=price_max,
        limit_bricks=limit_bricks,
        reverse=reverse,
    )

    resultado = controller.executar()

    if stats:
        exibir_stats(resultado)
        return

    if levels:
        exibir_levels(resultado)
        return

    if trend:
        exibir_trend(resultado)
        return

    exibir_renko(resultado, numerar=numerar)
