"""
Renko model institucional profissional.

✔ Ancoragem determinística por data
✔ Suporte candle e tick
✔ Compatível com controller atual
✔ Seguro para numpy arrays
✔ Funciona fora do pregão
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger
from ..conf import SESSION_OPEN

log = setup_logger(__name__)


# ==========================================================
# DATA STRUCTURE
# ==========================================================

@dataclass
class RenkoBrick:
    direction: str
    open: float
    close: float


# ==========================================================
# MODEL
# ==========================================================

class RenkoModel:

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size

    # ======================================================
    # AUXILIAR: descobrir último pregão real
    # ======================================================

    def _ultimo_pregao_data(self, timeframe):

        ultimo = mt5.copy_rates_from_pos(
            self.symbol,
            timeframe,
            0,
            1,
        )

        if ultimo is None or len(ultimo) == 0:
            return None

        ultimo_time = datetime.fromtimestamp(ultimo[0]["time"])
        return ultimo_time.date()

    # ======================================================
    # RATES (candle mode)
    # ======================================================

    def obter_rates(self, timeframe, quantidade: int, ancorar_abertura=False):

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                raise RuntimeError(f"Erro ao selecionar símbolo {self.symbol}")

            # -------------------------------------------------
            # SEM ANCORAGEM
            # -------------------------------------------------

            if not ancorar_abertura:

                if quantidade == 0:
                    quantidade = 1000

                rates = mt5.copy_rates_from_pos(
                    self.symbol,
                    timeframe,
                    0,
                    quantidade,
                )

                if rates is None:
                    return []

                return rates

            # -------------------------------------------------
            # COM ANCORAGEM REAL POR DATA
            # -------------------------------------------------

            data_pregao = self._ultimo_pregao_data(timeframe)

            if data_pregao is None:
                return []

            bruto = mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                5000,
            )

            if bruto is None or len(bruto) == 0:
                return []

            filtrado = []

            for r in bruto:
                r_time = datetime.fromtimestamp(r["time"])
                if r_time.date() == data_pregao:
                    filtrado.append(r)

            if not filtrado:
                return []

            total = len(filtrado)

            if quantidade == 0:
                return filtrado

            if quantidade >= total:
                return filtrado

            return filtrado[-quantidade:]

    # ======================================================
    # TICKS (tick mode)
    # ======================================================

    def obter_ticks(self, timeframe, max_ticks=5000):

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                raise RuntimeError(f"Erro ao selecionar símbolo {self.symbol}")

            data_pregao = self._ultimo_pregao_data(timeframe)

            if data_pregao is None:
                return []

            inicio = datetime.combine(
                data_pregao,
                datetime.strptime(SESSION_OPEN, "%H:%M").time(),
            )

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
    # CONSTRUÇÃO RENKO (CANDLE)
    # ======================================================

    def construir_renko(
        self,
        rates,
        modo="simples",
    ) -> List[RenkoBrick]:

        if rates is None or len(rates) < 2:
            return []

        bricks: List[RenkoBrick] = []

        last_price = float(rates[0]["open"])
        direction: Optional[str] = None

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            # -------------------------------------------------
            # MODO SIMPLES
            # -------------------------------------------------

            if modo == "simples":

                while high - last_price >= self.brick_size:
                    novo = last_price + self.brick_size
                    bricks.append(RenkoBrick("up", last_price, novo))
                    last_price = novo

                while last_price - low >= self.brick_size:
                    novo = last_price - self.brick_size
                    bricks.append(RenkoBrick("down", last_price, novo))
                    last_price = novo

            # -------------------------------------------------
            # MODO CLÁSSICO (reversão 2x)
            # -------------------------------------------------

            elif modo == "classico":

                if direction in (None, "up"):

                    while high - last_price >= self.brick_size:
                        novo = last_price + self.brick_size
                        bricks.append(RenkoBrick("up", last_price, novo))
                        last_price = novo
                        direction = "up"

                    if (
                        direction == "up"
                        and last_price - low >= 2 * self.brick_size
                    ):
                        novo = last_price - self.brick_size
                        bricks.append(RenkoBrick("down", last_price, novo))
                        last_price = novo
                        direction = "down"

                if direction in (None, "down"):

                    while last_price - low >= self.brick_size:
                        novo = last_price - self.brick_size
                        bricks.append(RenkoBrick("down", last_price, novo))
                        last_price = novo
                        direction = "down"

                    if (
                        direction == "down"
                        and high - last_price >= 2 * self.brick_size
                    ):
                        novo = last_price + self.brick_size
                        bricks.append(RenkoBrick("up", last_price, novo))
                        last_price = novo
                        direction = "up"

        return bricks

    # ======================================================
    # CONSTRUÇÃO RENKO (TICK)
    # ======================================================

    def construir_renko_ticks(self, ticks) -> List[RenkoBrick]:

        if ticks is None or len(ticks) < 2:
            return []

        bricks: List[RenkoBrick] = []

        last_price = float(ticks[0]["last"])

        for tick in ticks[1:]:

            price = float(tick["last"])

            while price - last_price >= self.brick_size:
                novo = last_price + self.brick_size
                bricks.append(RenkoBrick("up", last_price, novo))
                last_price = novo

            while last_price - price >= self.brick_size:
                novo = last_price - self.brick_size
                bricks.append(RenkoBrick("down", last_price, novo))
                last_price = novo

        return bricks
