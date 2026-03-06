"""
Renko view acessível.

Responsável por exibir os blocos Renko no terminal de forma simples,
compatível com leitores de tela e ambientes CLI.

Características
---------------

- Saída textual simples (sem gráficos ASCII complexos)
- Compatível com NVDA / JAWS
- Suporte a numeração opcional dos blocos
- Suporte a símbolos configuráveis para direção dos blocos

Os símbolos utilizados são definidos em `conf.py`:

    BRICK_UP
    BRICK_DOWN

Exemplo de saída:

    ▲ 128400 128460
    ▲ 128460 128520
    ▼ 128520 128460
"""

import click

from ..conf import DIGITS, BRICK_UP, BRICK_DOWN


# ==========================================================
# DETECÇÃO DE PADRÕES
# ==========================================================

def _detectar_padroes(bricks):
    """
    Detecta padrões simples de price action no Renko.

    Atualmente detecta:

    H1
        Primeira retomada de alta após correção.

    H2
        Segunda tentativa de continuação de alta.

    L2
        Segunda tentativa de continuação de baixa.
    """

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


# ==========================================================
# MÉTRICAS
# ==========================================================

def _metricas(bricks):
    """
    Calcula métricas básicas do gráfico Renko.

    Retorna
    -------
    tuple
        (up, down)
    """

    up = sum(1 for b in bricks if b.direction == "up")
    down = sum(1 for b in bricks if b.direction == "down")

    return up, down


# ==========================================================
# RENDERIZAÇÃO
# ==========================================================

def exibir_renko(resultado, numerar=False):
    """
    Exibe os blocos Renko no terminal.

    Parameters
    ----------
    resultado : list | RenkoTickResult
        Resultado retornado pelo RenkoModel.

        Pode ser:
        - lista simples de bricks
        - estrutura contendo `confirmados` e `em_formacao` (modo tick)

    numerar : bool
        Se True, adiciona numeração sequencial aos blocos.
    """

    if not resultado:
        click.echo("Nenhum bloco Renko gerado.")
        return

    em_formacao = None

    # compatível com retorno candle e tick
    if isinstance(resultado, list):
        bricks = resultado
    else:
        bricks = resultado.confirmados
        em_formacao = resultado.em_formacao

    click.echo("=== GRAFICO RENKO ===")
    click.echo(f"Total de blocos: {len(bricks)}")
    click.echo()

    # ------------------------------------------------------
    # MÉTRICAS
    # ------------------------------------------------------

    up, down = _metricas(bricks)

    click.echo("METRICAS:")
    click.echo(f"Up: {up}")
    click.echo(f"Down: {down}")
    click.echo(f"Delta: {up - down}")
    click.echo()

    # ------------------------------------------------------
    # PADRÕES
    # ------------------------------------------------------

    patterns = _detectar_padroes(bricks)

    if patterns:
        click.echo("PADROES:")
        for p in patterns:
            click.echo(p)
        click.echo()

    # ------------------------------------------------------
    # BLOCOS CONFIRMADOS
    # ------------------------------------------------------

    for i, brick in enumerate(bricks, start=1):

        if brick.direction == "up":
            simbolo = BRICK_UP
        else:
            simbolo = BRICK_DOWN

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

    # ------------------------------------------------------
    # BLOCO EM FORMAÇÃO (modo híbrido)
    # ------------------------------------------------------

    if em_formacao:

        click.echo()

        if em_formacao.direction == "up":
            simbolo = BRICK_UP
        else:
            simbolo = BRICK_DOWN

        linha = (
            f"FORMANDO {simbolo} "
            f"{em_formacao.open:.{DIGITS}f} "
            f"{em_formacao.close:.{DIGITS}f}"
        )

        click.echo(linha)
