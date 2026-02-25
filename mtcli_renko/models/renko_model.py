"""
Renko model institucional profissional.

✔ Candle mode determinístico
✔ Tick mode híbrido (confirmados + em formação)
✔ Estrutura estável
✔ Compatível com controller atual
"""

from dataclasses import dataclass
from typing import List, Optional, NamedTuple
from datetime import datetime

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger
from ..conf import SESSION_OPEN

log = setup_logger(__name__)


# ==========================================================
# DATA STRUCTURES
# ==========================================================

@dataclass
class RenkoBrick:
    direction: str
    open: float
    close: float


class RenkoResult(NamedTuple):
    confirmados: List[RenkoBrick]
    em_formacao: Optional[RenkoBrick]


# ==========================================================
# MODEL
# ==========================================================

class RenkoModel:

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size

    # ======================================================
    # AUXILIAR
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

            if not ancorar_abertura:

                if quantidade == 0:
                    quantidade = 1000

                rates = mt5.copy_rates_from_pos(
                    self.symbol,
                    timeframe,
                    0,
                    quantidade,
                )

                return rates or []

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

            if quantidade == 0:
                return filtrado

            return filtrado[-quantidade:]

    # ======================================================
    # TICKS
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

            agora = datetime.now()

            ticks = mt5.copy_ticks_range(
                self.symbol,
                inicio,
                agora,
                mt5.COPY_TICKS_ALL,
            )

            if ticks is None or len(ticks) == 0:
                return []

            if len(ticks) > max_ticks:
                ticks = ticks[-max_ticks:]

            return ticks

    # ======================================================
    # CONSTRUÇÃO RENKO (CANDLE)
    # ======================================================

    def construir_renko(self, rates, modo="simples") -> List[RenkoBrick]:

        if rates is None or len(rates) < 2:
            return []

        bricks: List[RenkoBrick] = []
        last_price = float(rates[0]["open"])

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

    # ======================================================
    # CONSTRUÇÃO RENKO (TICK HÍBRIDO)
    # ======================================================

    def construir_renko_ticks(self, ticks) -> RenkoResult:

        if ticks is None or len(ticks) < 2:
            return RenkoResult([], None)

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

        # ----------------------------
        # Brick em formação
        # ----------------------------

        ultimo_preco = float(ticks[-1]["last"])
        diferenca = ultimo_preco - last_price

        em_formacao = None

        if abs(diferenca) > 0:

            direcao = "up" if diferenca > 0 else "down"

            em_formacao = RenkoBrick(
                direction=direcao,
                open=last_price,
                close=ultimo_preco,
            )

        return RenkoResult(
            confirmados=bricks,
            em_formacao=em_formacao,
        )
