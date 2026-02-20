"""
Renko view.

Saída textual acessível para leitores de tela.
"""

def exibir_renko(bricks):
    """
    Exibe blocos Renko em formato textual linear.

    :param bricks: lista de RenkoBrick
    """

    if not bricks:
        print("Nenhum bloco Renko gerado.")
        return

    print("=== GRAFICO RENKO ===")
    print(f"Total de blocos: {len(bricks)}")
    print()

    for i, brick in enumerate(bricks, start=1):
        print(
            f"Bloco {i}: "
            f"Direcao: {brick.direction.upper()} | "
            f"Abertura: {brick.open:.2f} | "
            f"Fechamento: {brick.close:.2f}"
        )
