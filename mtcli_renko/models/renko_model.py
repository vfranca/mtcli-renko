"""
RenkoModel.

Responsável por:
- Construir Renko a partir de candles
- Construir Renko a partir de ticks
- Integrar com TickRepository (SQLite + cache)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import MetaTrader5 as mt5

from mtcli.marketdata.tick_repository import TickRepository


# =========================
# ENTIDADES
# =========================

@dataclass
class Brick:
    direction: str
    open: float
    close: float


@dataclass
class RenkoTickResult:
    confirmados: List[Brick]
    em_formacao: Optional[Brick] = None


# =========================
# MODEL
# =========================

class RenkoModel:

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size
        self.repo = TickRepository()

    # ============================================================
    # CANDLE MODE
    # ============================================================

    def obter_rates(self, timeframe, quantidade, ancorar_abertura=False):

        rates = mt5.copy_rates_from_pos(
            self.symbol,
            timeframe,
            0,
            quantidade,
        )

        return rates

    def construir_renko(self, rates, modo="simples"):

        if rates is None or len(rates) == 0:
            return []

        bricks = []

        preco_base = rates[0]["close"]

        for candle in rates:
            preco = candle["close"]

            while preco >= preco_base + self.brick_size:
                novo = Brick("up", preco_base, preco_base + self.brick_size)
                bricks.append(novo)
                preco_base += self.brick_size

            while preco <= preco_base - self.brick_size:
                novo = Brick("down", preco_base, preco_base - self.brick_size)
                bricks.append(novo)
                preco_base -= self.brick_size

        return bricks

    # ============================================================
    # TICK MODE (COM INTEGRAÇÃO SQLITE)
    # ============================================================

    def obter_ticks(self, timeframe=None, max_ticks=10000):
        """
        Sincroniza com banco e retorna ticks recentes.
        """

        # Atualiza banco com delta
        self.repo.sync(self.symbol)

        # Define janela recente
        end_ts = int(datetime.now().timestamp())
        start_ts = end_ts - (60 * 60 * 24)  # últimas 24h

        rows = self.repo.get_ticks_between(
            self.symbol,
            start_ts,
            end_ts,
        )

        if not rows:
            return []

        return rows[-max_ticks:]

    # ============================================================
    # CONSTRUÇÃO RENKO A PARTIR DE TICKS
    # ============================================================

    def construir_renko_ticks(self, ticks) -> RenkoTickResult:

        if not ticks:
            return RenkoTickResult([])

        bricks: List[Brick] = []

        # ticks = (time, bid, ask, last, volume, flags)
        preco_base = ticks[0][3]  # last

        ultimo_preco = preco_base

        for tick in ticks:
            preco = tick[3]  # last

            # Movimento de alta
            while preco >= preco_base + self.brick_size:
                novo = Brick("up", preco_base, preco_base + self.brick_size)
                bricks.append(novo)
                preco_base += self.brick_size

            # Movimento de baixa
            while preco <= preco_base - self.brick_size:
                novo = Brick("down", preco_base, preco_base - self.brick_size)
                bricks.append(novo)
                preco_base -= self.brick_size

            ultimo_preco = preco

        # Brick parcial (em formação)
        diferenca = ultimo_preco - preco_base

        if abs(diferenca) > 0:
            direction = "up" if diferenca > 0 else "down"
            em_formacao = Brick(direction, preco_base, ultimo_preco)
        else:
            em_formacao = None

        return RenkoTickResult(confirmados=bricks, em_formacao=em_formacao)
