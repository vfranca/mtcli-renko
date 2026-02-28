"""
Renko view acessível.
"""

import click
from ..conf import DIGITS


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

    if isinstance(resultado, list):

        bricks = resultado

    else:

        bricks = resultado.confirmados

    click.echo("=== GRAFICO RENKO ===")
    click.echo(f"Total de blocos: {len(bricks)}")
    click.echo()

    up, down = _metricas(bricks)

    click.echo("METRICAS:")
    click.echo(f"Up: {up}")
    click.echo(f"Down: {down}")
    click.echo(f"Delta: {up-down}")
    click.echo()

    patterns = _detectar_padroes(bricks)

    if patterns:
        click.echo("PADROES:")
        for p in patterns:
            click.echo(p)
        click.echo()

    for i, brick in enumerate(bricks, start=1):

        if numerar:
            linha = f"{i} {brick.direction.upper()} {brick.open:.{DIGITS}f} {brick.close:.{DIGITS}f}"
        else:
            linha = f"{brick.direction.upper()} {brick.open:.{DIGITS}f} {brick.close:.{DIGITS}f}"

        click.echo(linha)
