"""
Renko model institucional com suporte Candle e Tick.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger

log = setup_logger(__name__)


@dataclass
class RenkoBrick:
    direction: str
    open: float
    close: float


class RenkoModel:

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size

    # ======================================================
    # TICKS
    # ======================================================

    def obter_ticks(self, max_ticks=3000):

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                raise RuntimeError(f"Erro ao selecionar símbolo {self.symbol}")

            inicio = datetime.now() - timedelta(minutes=10)

            ticks = mt5.copy_ticks_from(
                self.symbol,
                inicio,
                max_ticks,
                mt5.COPY_TICKS_ALL,
            )

            if ticks is None:
                return []

            return ticks

    # ======================================================
    # RATES (mantido igual ao seu)
    # ======================================================

    def obter_rates(self, timeframe, quantidade: int, ancorar_abertura=False):

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                raise RuntimeError(f"Erro ao selecionar símbolo {self.symbol}")

            if quantidade == 0:
                quantidade = 1000

            return mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                quantidade,
            )

    # ======================================================
    # CONSTRUÇÃO TICK-BASED
    # ======================================================

    def construir_renko_ticks(self, ticks, modo="simples"):

        if not ticks or len(ticks) < 2:
            return []

        bricks: List[RenkoBrick] = []

        last_price = float(ticks[0]["last"])
        direction: Optional[str] = None

        for tick in ticks[1:]:

            price = float(tick["last"])

            # UP
            while price - last_price >= self.brick_size:
                novo = last_price + self.brick_size
                bricks.append(RenkoBrick("up", last_price, novo))
                last_price = novo
                direction = "up"

            # DOWN
            while last_price - price >= self.brick_size:
                novo = last_price - self.brick_size
                bricks.append(RenkoBrick("down", last_price, novo))
                last_price = novo
                direction = "down"

        return bricks

    # ======================================================
    # CONSTRUÇÃO CANDLE-BASED (SEU ORIGINAL)
    # ======================================================

    def construir_renko(
        self,
        rates,
        modo="simples",
        ancorar_abertura=False,
    ) -> List[RenkoBrick]:

        if not rates or len(rates) < 2:
            return []

        bricks: List[RenkoBrick] = []

        last_price = float(rates[0]["close"])

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            while high - last_price >= self.brick_size:
                novo = last_price + self.brick_size
                bricks.append(RenkoBrick("up", last_price, novo))
                last_price = novo

            while last_price - low >= self.brick_size:
                novo = last_price - self.brick_size
                bricks.append(RenkoBrick("down", last_price, novo))
                last_price = novo

        return bricks
