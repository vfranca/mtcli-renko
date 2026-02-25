"""
Renko view acessível.
"""

import click
from ..conf import DIGITS


def exibir_renko(resultado, numerar: bool = False):

    if not resultado:
        click.echo("Nenhum bloco Renko gerado.")
        return

    # Lista simples (estrutural ou agressivo)
    if isinstance(resultado, list):

        click.echo("=== GRAFICO RENKO ===")
        click.echo(f"Total de blocos: {len(resultado)}")
        click.echo()

        for i, brick in enumerate(resultado, start=1):

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

        return

    # Híbrido
    confirmados = resultado.confirmados
    em_formacao = resultado.em_formacao

    click.echo("=== GRAFICO RENKO ===")
    click.echo(f"Blocos confirmados: {len(confirmados)}")
    click.echo()

    for i, brick in enumerate(confirmados, start=1):

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

    if em_formacao:
        click.echo()
        click.echo("EM FORMACAO:")
        click.echo(
            f"{em_formacao.direction.upper()} "
            f"{em_formacao.open:.{DIGITS}f} "
            f"{em_formacao.close:.{DIGITS}f}"
        )
