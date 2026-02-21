"""
Renko view.

Saída textual acessível para leitores de tela.
"""

import click
from ..conf import DIGITS


def exibir_renko(bricks, numerar: bool = False):
    """
    Exibe blocos Renko em formato textual linear.

    :param bricks: lista de RenkoBrick
    :param numerar: se True, exibe índice das linhas
    """

    if not bricks:
        click.echo("Nenhum bloco Renko gerado.")
        return

    click.echo("=== GRAFICO RENKO ===")
    click.echo(f"Total de blocos: {len(bricks)}")
    click.echo()

    for i, brick in enumerate(bricks, start=1):

        if numerar:
            linha = (
                f"{i} "
                f"{brick.direction.upper()} "
                f"{brick.open:.{DIGITS}f} "
                f"{brick.close:.{DIGITS}f}"
            )
        else:
            linha = (
                f"{brick.direction.upper()} "
                f"{brick.open:.{DIGITS}f} "
                f"{brick.close:.{DIGITS}f}"
            )

        click.echo(linha)
