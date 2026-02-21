"""
Renko view.

Saída textual acessível para leitores de tela.
"""

import click
from ..conf import DIGITS


def exibir_renko(bricks):
    """
    Exibe blocos Renko em formato textual linear.

    :param bricks: lista de RenkoBrick
    """

    if not bricks:
        click.echo("Nenhum bloco Renko gerado.")
        return

    click.echo("=== GRAFICO RENKO ===")
    click.echo(f"Total de blocos: {len(bricks)}")
    click.echo()

    for i, brick in enumerate(bricks, start=1):
        click.echo(
            f"{i} "
            f"{brick.direction.upper()} "
            f"{brick.open:.{DIGITS}f} "
            f"{brick.close:.{DIGITS}f}"
        )
