"""
RenkoModel profissional com:

- Ancoragem correta em múltiplos do brick
- Suporte real a ancorar_abertura
- Integração SQLite + MT5
- Determinismo estrutural
"""

from dataclasses import dataclass
from datetime import datetime, time as dtime
from typing import List, Optional

import MetaTrader5 as mt5

from mtcli.marketdata.tick_repository import TickRepository
from ..conf import SESSION_OPEN


# ============================================================
# ENTIDADES
# ============================================================

@dataclass
class Brick:
    direction: str
    open: float
    close: float


@dataclass
class RenkoTickResult:
    confirmados: List[Brick]
    em_formacao: Optional[Brick] = None


# ============================================================
# MODEL
# ============================================================

class RenkoModel:

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size
        self.repo = TickRepository()

    # ============================================================
    # UTIL
    # ============================================================

    def _align_price(self, price: float) -> float:
        """
        Alinha preço ao múltiplo do brick.
        """
        return round(price / self.brick_size) * self.brick_size

    def _session_start_from_timestamp(self, ts: int) -> int:
        """
        Calcula abertura da sessão baseada na data do timestamp.
        """

        dt = datetime.fromtimestamp(ts)

        abertura = datetime.combine(
            dt.date(),
            dtime.fromisoformat(SESSION_OPEN)
        )

        return int(abertura.timestamp())

    # ============================================================
    # CANDLE MODE
    # ============================================================

    def obter_rates(self, timeframe, quantidade, ancorar_abertura=False):

        if quantidade == 0:
            quantidade = 500

        rates = mt5.copy_rates_from_pos(
            self.symbol,
            timeframe,
            0,
            quantidade,
        )

        if rates is None or len(rates) == 0:
            return []

        if ancorar_abertura:
            rates = self._filtrar_sessao(rates)

        return rates

    def _filtrar_sessao(self, rates):

        abertura = dtime.fromisoformat(SESSION_OPEN)

        filtrados = []

        for r in rates:

            ts = datetime.fromtimestamp(r["time"])

            if ts.time() >= abertura:
                filtrados.append(r)

        return filtrados

    def _get_close_from_rate(self, candle):

        try:
            return candle["close"]

        except Exception:

            try:
                return candle.close

            except Exception:
                return candle[4]

    def construir_renko(self, rates, modo="simples"):

        if not rates:
            return []

        bricks: List[Brick] = []

        preco_inicial = self._get_close_from_rate(rates[0])
        preco_base = self._align_price(preco_inicial)

        for candle in rates:

            preco = self._get_close_from_rate(candle)

            while preco >= preco_base + self.brick_size:

                bricks.append(
                    Brick("up", preco_base, preco_base + self.brick_size)
                )

                preco_base += self.brick_size

            while preco <= preco_base - self.brick_size:

                bricks.append(
                    Brick("down", preco_base, preco_base - self.brick_size)
                )

                preco_base -= self.brick_size

        return bricks

    # ============================================================
    # TICK MODE
    # ============================================================

    def obter_ticks(self, timeframe=None, max_ticks=10000, ancorar_abertura=False):

        last_time = self.repo._get_last_tick_time(self.symbol)

        if last_time is None:
            self.repo.sync(self.symbol, days_back=3)
        else:
            self.repo.sync(self.symbol)

        rows = self.repo.get_ticks_between(
            self.symbol,
            0,
            int(datetime.now().timestamp()),
        )

        if not rows:
            return []

        # ========================================================
        # ANCORAGEM NA ABERTURA DA SESSÃO ATUAL
        # ========================================================

        if ancorar_abertura:

            ultimo_tick_ts = rows[-1][0]

            start_ts = self._session_start_from_timestamp(ultimo_tick_ts)

            rows = [t for t in rows if t[0] >= start_ts]

        return rows[-max_ticks:]

    # ============================================================
    # CONSTRUÇÃO RENKO
    # ============================================================

    def construir_renko_ticks(self, ticks) -> RenkoTickResult:

        if not ticks:
            return RenkoTickResult([])

        bricks: List[Brick] = []

        preco_inicial = ticks[0][3]
        preco_base = self._align_price(preco_inicial)

        ultimo_preco = preco_base

        for tick in ticks:

            preco = tick[3]

            while preco >= preco_base + self.brick_size:

                bricks.append(
                    Brick("up", preco_base, preco_base + self.brick_size)
                )

                preco_base += self.brick_size

            while preco <= preco_base - self.brick_size:

                bricks.append(
                    Brick("down", preco_base, preco_base - self.brick_size)
                )

                preco_base -= self.brick_size

            ultimo_preco = preco

        diferenca = ultimo_preco - preco_base

        if abs(diferenca) > 0:

            direction = "up" if diferenca > 0 else "down"

            em_formacao = Brick(
                direction,
                preco_base,
                ultimo_preco,
            )

        else:

            em_formacao = None

        return RenkoTickResult(
            confirmados=bricks,
            em_formacao=em_formacao,
        )
