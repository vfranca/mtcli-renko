"""
Utilitários de análise de Renko.
"""

from collections import Counter


def _get_bricks(resultado):

    if hasattr(resultado, "confirmados"):
        return resultado.confirmados

    return resultado


# ==========================================================
# STATS
# ==========================================================

def exibir_stats(resultado):

    bricks = _get_bricks(resultado)

    if not bricks:
        print("Nenhum brick gerado.")
        return

    direcoes = [b.direction for b in bricks]

    c = Counter(direcoes)

    up = c.get("up", 0)
    down = c.get("down", 0)

    amplitude = abs(bricks[-1].close - bricks[0].open)

    print()
    print("Renko Stats")
    print("-" * 28)
    print(f"Bricks: {len(bricks)}")
    print(f"Up bricks: {up}")
    print(f"Down bricks: {down}")
    print(f"Preço atual: {bricks[-1].close}")
    print(f"Amplitude total: {amplitude}")
    print()


# ==========================================================
# LEVELS
# ==========================================================

def exibir_levels(resultado):

    bricks = _get_bricks(resultado)

    if not bricks:
        print("Nenhum brick.")
        return

    topo = max(b.close for b in bricks)
    fundo = min(b.close for b in bricks)

    reversao = bricks[-2].close if len(bricks) > 1 else None

    print()
    print("Renko Levels")
    print("-" * 28)
    print(f"Topo atual: {topo}")
    print(f"Fundo atual: {fundo}")
    print(f"Range atual: {topo - fundo}")

    if reversao:
        print(f"Última reversão: {reversao}")

    print()


# ==========================================================
# TREND
# ==========================================================

def exibir_trend(resultado):

    bricks = _get_bricks(resultado)

    if not bricks:
        print("Sem dados.")
        return

    last = bricks[-1]

    print()
    print("Trend")
    print("-" * 28)
    print(f"Direção: {last.direction.upper()}")
    print(f"Último preço: {last.close}")
    print()
