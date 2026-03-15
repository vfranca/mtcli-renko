"""
Renko view acessível.
"""

import click

from ..conf import DIGITS, BRICK_UP, BRICK_DOWN


def _detectar_padroes(bricks):

    if len(bricks) < 3:
        return []

    patterns = []

    last = bricks[-1].direction
    prev = bricks[-2].direction
    prev2 = bricks[-3].direction

    if last == "up" and prev == "down":
        patterns.append("H1")

    if last == "up" and prev == "down" and prev2 == "up":
        patterns.append("H2")

    if last == "down" and prev == "up" and prev2 == "down":
        patterns.append("L2")

    return patterns


def _metricas(bricks):

    up = sum(1 for b in bricks if b.direction == "up")
    down = sum(1 for b in bricks if b.direction == "down")

    return up, down


def exibir_renko(resultado, numerar=False):

    if not resultado:
        click.echo("Nenhum bloco Renko gerado.")
        return

    em_formacao = None

    if isinstance(resultado, list):
        bricks = resultado
    else:
        bricks = resultado.confirmados
        em_formacao = resultado.em_formacao

    click.echo("RENKO")
    click.echo(f"Blocos: {len(bricks)}")
    click.echo()

    up, down = _metricas(bricks)

    click.echo(f"Up: {up}")
    click.echo(f"Down: {down}")
    click.echo(f"Delta: {up - down}")
    click.echo()

    patterns = _detectar_padroes(bricks)

    if patterns:
        click.echo("Padroes:")
        for p in patterns:
            click.echo(p)
        click.echo()

    for i, brick in enumerate(bricks, start=1):

        simbolo = BRICK_UP if brick.direction == "up" else BRICK_DOWN

        if numerar:
            linha = (
                f"{i} {simbolo} "
                f"{brick.open:.{DIGITS}f} "
                f"{brick.close:.{DIGITS}f}"
            )
        else:
            linha = (
                f"{simbolo} "
                f"{brick.open:.{DIGITS}f} "
                f"{brick.close:.{DIGITS}f}"
            )

        click.echo(linha)

    if em_formacao:

        click.echo()

        simbolo = BRICK_UP if em_formacao.direction == "up" else BRICK_DOWN

        linha = (
            f"FORMANDO {simbolo} "
            f"{em_formacao.open:.{DIGITS}f} "
            f"{em_formacao.close:.{DIGITS}f}"
        )

        click.echo(linha)
