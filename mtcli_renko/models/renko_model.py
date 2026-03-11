"""
RenkoModel profissional.

Candle mode determinístico
Tick mode híbrido (confirmados + em formação)
Ancoragem correta na abertura da B3
Ajuste UTC da corretora
Margem de segurança na abertura
Reconstrução de caminho do candle (path reconstruction)
Compatível com controller atual
Funciona mesmo com mercado fechado
"""

from dataclasses import dataclass
from typing import List, Optional, NamedTuple
from datetime import datetime, time as dtime, timedelta

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger
from mtcli.marketdata.tick_repository import TickRepository
from ..conf import SESSION_OPEN, SESSION_OPEN_OFFSET_SECONDS, BROKER_UTC_OFFSET

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
    # UTIL
    # ======================================================

    def _session_start_timestamp(self, data):
        """
        Retorna timestamp da abertura da sessão em milissegundos.
        """

        abertura_b3 = datetime.combine(
            data,
            dtime.fromisoformat(SESSION_OPEN),
        )

        abertura_utc = abertura_b3 + timedelta(hours=BROKER_UTC_OFFSET)

        abertura_utc += timedelta(seconds=SESSION_OPEN_OFFSET_SECONDS)

        return int(abertura_utc.timestamp() * 1000)

    # ======================================================
    # RATES (CANDLE MODE)
    # ======================================================

    def obter_rates(self, timeframe, quantidade, ancorar_abertura=False):

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

        ultimo_ts = int(rates[-1]["time"])

        ultimo_dia = datetime.utcfromtimestamp(ultimo_ts).date()

        abertura_ts = int(self._session_start_timestamp(ultimo_dia) / 1000)

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
        """
        Obtém ticks do banco SQLite.

        Sem ancoragem:
            retorna os últimos N ticks.

        Com ancoragem (--ancorar-abertura):
            retorna os ticks da sessão do último pregão
            disponível no banco.
        """

        last_time = self.repo._get_last_tick_msc(self.symbol)

        if last_time is None:
            raise RuntimeError(
                "Nenhum tick disponível no banco.\n"
                "Execute primeiro:\n"
                "mt ticks SYMBOL"
            )

        # ----------------------------
        # modo normal (últimos ticks)
        # ----------------------------

        if not ancorar_abertura:

            ticks = self.repo.get_last_ticks(
                self.symbol,
                max_ticks,
            )

            if ticks is None or len(ticks) == 0:
                return []

            return ticks

        # -----------------------------------
        # modo ancorado na abertura da sessão
        # -----------------------------------

        # usa o último tick do banco para determinar a sessão
        data = datetime.utcfromtimestamp(last_time / 1000).date()

        start_ts = self._session_start_timestamp(data)

        ticks = self.repo.get_ticks_between(
            self.symbol,
            start_ts,
            last_time,
        )

        if ticks is None or len(ticks) == 0:
            return []

        return ticks

    # ======================================================
    # PATH RECONSTRUCTION
    # ======================================================

    def _reconstruir_path(self, rate):

        o = float(rate["open"])
        h = float(rate["high"])
        l = float(rate["low"])
        c = float(rate["close"])

        if c >= o:
            return [o, l, h, c]

        return [o, h, l, c]

    # ======================================================
    # RENKO CANDLE
    # ======================================================

    def construir_renko(self, rates, modo="simples") -> List[Brick]:

        if rates is None or len(rates) < 2:
            return []

        bricks: List[Brick] = []

        last_price = float(rates[0]["open"])

        for rate in rates[1:]:

            path = self._reconstruir_path(rate)

            for price in path:

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

        # brick em formação

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
