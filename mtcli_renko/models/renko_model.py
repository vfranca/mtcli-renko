"""
RenkoModel profissional.

✔ Candle mode determinístico
✔ Tick mode híbrido (confirmados + em formação)
✔ Compatível com controller atual
✔ Funciona mesmo com mercado fechado
✔ Correção de numpy truth value
✔ Ancoragem estável na sessão
"""

from dataclasses import dataclass
from typing import List, Optional, NamedTuple
from datetime import datetime, time as dtime

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger
from mtcli.marketdata.tick_repository import TickRepository
from ..conf import SESSION_OPEN

log = setup_logger(__name__)


# ==========================================================
# DATA STRUCTURES
# ==========================================================

@dataclass
class Brick:
    direction: str
    open: float
    close: float


class RenkoTickResult(NamedTuple):
    confirmados: List[Brick]
    em_formacao: Optional[Brick]


# ==========================================================
# MODEL
# ==========================================================

class RenkoModel:

    def __init__(self, symbol: str, brick_size: float):

        self.symbol = symbol
        self.brick_size = brick_size
        self.repo = TickRepository()

    # ======================================================
    # AUXILIAR
    # ======================================================

    def _ultimo_pregao_data(self, timeframe):

        with mt5_conexao():

            ultimo = mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                1,
            )

        if ultimo is None or len(ultimo) == 0:
            return None

        ultimo_time = datetime.fromtimestamp(int(ultimo[0]["time"]))
        return ultimo_time.date()

    # ======================================================
    # RATES (CANDLE MODE)
    # ======================================================

    def obter_rates(self, timeframe, quantidade, ancorar_abertura=False):
        """
        Obtém candles do MT5.

        Se ancorar_abertura=True:
        retorna apenas candles da sessão do último pregão disponível.
        """

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                raise RuntimeError(f"Erro ao selecionar símbolo {self.symbol}")

            if quantidade == 0:
                quantidade = 1000

            rates = mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                quantidade,
            )

        if rates is None or len(rates) == 0:
            return []

        if not ancorar_abertura:
            return rates

        # ----------------------------------------------------
        # ANCORAGEM NA ÚLTIMA SESSÃO DISPONÍVEL
        # ----------------------------------------------------

        ultimo_ts = int(rates[-1]["time"])
        ultimo_dia = datetime.fromtimestamp(ultimo_ts).date()

        abertura = datetime.combine(
            ultimo_dia,
            dtime.fromisoformat(SESSION_OPEN),
        )

        abertura_ts = int(abertura.timestamp())

        filtrados = []

        for r in rates:

            ts = int(r["time"])

            if ts >= abertura_ts:
                filtrados.append(r)

        return filtrados

    # ======================================================
    # TICKS (BANCO + MT5)
    # ======================================================

    def obter_ticks(self, max_ticks=5000, ancorar_abertura=False):

        last_time = self.repo._get_last_tick_time(self.symbol)

        if last_time is None:

            self.repo.sync(self.symbol, days_back=3)
            last_time = self.repo._get_last_tick_time(self.symbol)

        else:

            self.repo.sync(self.symbol)

        if last_time is None:
            return []

        end_ts = int(datetime.now().timestamp())

        if ancorar_abertura:

            data = datetime.fromtimestamp(last_time)

            abertura = datetime.combine(
                data.date(),
                datetime.strptime(SESSION_OPEN, "%H:%M").time(),
            )

            start_ts = int(abertura.timestamp())

        else:

            start_ts = 0

        rows = self.repo.get_ticks_between(
            self.symbol,
            start_ts,
            end_ts,
        )

        if rows is None or len(rows) == 0:
            return []

        return rows[-max_ticks:]

    # ======================================================
    # RENKO CANDLE
    # ======================================================

    def construir_renko(self, rates, modo="simples") -> List[Brick]:

        if rates is None or len(rates) < 2:
            return []

        bricks: List[Brick] = []

        last_price = float(rates[0]["open"])

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            while high - last_price >= self.brick_size:

                novo = last_price + self.brick_size

                bricks.append(
                    Brick(
                        direction="up",
                        open=last_price,
                        close=novo,
                    )
                )

                last_price = novo

            while last_price - low >= self.brick_size:

                novo = last_price - self.brick_size

                bricks.append(
                    Brick(
                        direction="down",
                        open=last_price,
                        close=novo,
                    )
                )

                last_price = novo

        return bricks

    # ======================================================
    # RENKO TICK MODE
    # ======================================================

    def construir_renko_ticks(self, ticks) -> RenkoTickResult:

        if ticks is None or len(ticks) < 2:
            return RenkoTickResult([], None)

        bricks: List[Brick] = []

        last_price = float(ticks[0][3])

        for tick in ticks[1:]:

            price = float(tick[3])

            while price - last_price >= self.brick_size:

                novo = last_price + self.brick_size

                bricks.append(
                    Brick("up", last_price, novo)
                )

                last_price = novo

            while last_price - price >= self.brick_size:

                novo = last_price - self.brick_size

                bricks.append(
                    Brick("down", last_price, novo)
                )

                last_price = novo

        # ------------------------------------------
        # brick em formação
        # ------------------------------------------

        ultimo_preco = float(ticks[-1][3])

        diferenca = ultimo_preco - last_price

        em_formacao = None

        if abs(diferenca) > 0:

            direcao = "up" if diferenca > 0 else "down"

            em_formacao = Brick(
                direction=direcao,
                open=last_price,
                close=ultimo_preco,
            )

        return RenkoTickResult(
            confirmados=bricks,
            em_formacao=em_formacao,
        )
