"""
Renko model do plugin mtcli-renko.

Responsável por:

Coleta de dados do MetaTrader 5
Filtragem de dados da sessão
Construção de blocos Renko
Suporte a modo candle e modo tick

Características:

Renko determinístico em candle mode
Renko híbrido em tick mode
Brick em formação em tempo real
Compatível com arquitetura MVC do mtcli
"""

from dataclasses import dataclass
from typing import List, Optional, NamedTuple
from datetime import datetime, timedelta

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger

from ..conf import (
    SESSION_OPEN,
    SESSION_OPEN_OFFSET_SECONDS,
    BROKER_UTC_OFFSET,
)

log = setup_logger(__name__)


# ==========================================================
# DATA STRUCTURES
# ==========================================================

@dataclass
class RenkoBrick:
    """
    Representa um bloco Renko.

    Attributes
    ----------
    direction : str
        Direção do bloco ("up" ou "down")

    open : float
        Preço de abertura do bloco.

    close : float
        Preço de fechamento do bloco.
    """

    direction: str
    open: float
    close: float


class RenkoResult(NamedTuple):
    """
    Resultado da construção Renko em modo tick.

    Attributes
    ----------
    confirmados : list[RenkoBrick]
        Lista de blocos já confirmados.

    em_formacao : RenkoBrick | None
        Bloco parcial ainda em formação.
    """

    confirmados: List[RenkoBrick]
    em_formacao: Optional[RenkoBrick]


# ==========================================================
# MODEL
# ==========================================================

class RenkoModel:
    """
    Modelo responsável pela construção do gráfico Renko.
    """

    MAX_BRICKS_PER_TICK = 500

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size

    # ======================================================
    # UTILIDADES
    # ======================================================

    def _ultimo_pregao_data(self, timeframe):
        """
        Obtém a data do último pregão disponível.
        """

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

    def _calcular_abertura(self, data_pregao):
        """
        Calcula o horário de abertura da sessão considerando:

        horário oficial da bolsa
        offset UTC da corretora
        offset adicional de segurança
        """

        hora = datetime.strptime(SESSION_OPEN, "%H:%M")

        abertura = datetime.combine(
            data_pregao,
            hora.time(),
        )

        abertura += timedelta(hours=BROKER_UTC_OFFSET)
        abertura += timedelta(seconds=SESSION_OPEN_OFFSET_SECONDS)

        return abertura

    # ======================================================
    # RATES (CANDLE MODE)
    # ======================================================

    def obter_rates(self, timeframe, quantidade: int, ancorar_abertura=False):
        """
        Obtém candles do MetaTrader 5.
        """

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

            abertura = self._calcular_abertura(data_pregao)

            bruto = mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                999,
            )

            if bruto is None:
                return []

            filtrado = []

            for r in bruto:

                r_time = datetime.fromtimestamp(r["time"])

                if r_time >= abertura:
                    filtrado.append(r)

            if quantidade == 0:
                return filtrado

            return filtrado[-quantidade:]

    # ======================================================
    # TICKS
    # ======================================================

    def obter_ticks(self, max_ticks=5000, ancorar_abertura=False):
        """
        Obtém ticks do MetaTrader 5.

        Parameters
        ----------
        max_ticks : int
            Número máximo de ticks retornados.

        ancorar_abertura : bool
            Se True, filtra ticks a partir da abertura da sessão.
        """

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                raise RuntimeError(f"Erro ao selecionar símbolo {self.symbol}")

            agora = datetime.utcnow()

            # ------------------------------------------
            # definir início
            # ------------------------------------------

            if ancorar_abertura:

                data = agora.date()

                abertura = datetime.combine(
                    data,
                    datetime.strptime(SESSION_OPEN, "%H:%M").time(),
                )

                abertura += timedelta(hours=BROKER_UTC_OFFSET)
                abertura += timedelta(seconds=SESSION_OPEN_OFFSET_SECONDS)

                inicio = abertura

            else:

                inicio = agora - timedelta(hours=24)

            # ------------------------------------------
            # obter ticks
            # ------------------------------------------

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
    # RENKO CANDLE
    # ======================================================

    def construir_renko(self, rates, modo="simples") -> List[RenkoBrick]:
        """
        Constrói blocos Renko a partir de candles.
        """

        if rates is None or len(rates) < 2:
            return []

        bricks: List[RenkoBrick] = []

        last_price = float(rates[0]["open"])

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            count = 0

            while high - last_price >= self.brick_size:

                novo = last_price + self.brick_size

                bricks.append(RenkoBrick("up", last_price, novo))

                last_price = novo

                count += 1

                if count > self.MAX_BRICKS_PER_TICK:
                    break

            count = 0

            while last_price - low >= self.brick_size:

                novo = last_price - self.brick_size

                bricks.append(RenkoBrick("down", last_price, novo))

                last_price = novo

                count += 1

                if count > self.MAX_BRICKS_PER_TICK:
                    break

        return bricks

    # ======================================================
    # RENKO TICKS
    # ======================================================

    def construir_renko_ticks(self, ticks) -> RenkoResult:
        """
        Constrói Renko baseado em ticks.
        """

        if ticks is None or len(ticks) < 2:
            return RenkoResult([], None)

        bricks: List[RenkoBrick] = []

        last_price = float(ticks[0]["last"])

        for tick in ticks[1:]:

            price = float(tick["last"])

            count = 0

            while price - last_price >= self.brick_size:

                novo = last_price + self.brick_size

                bricks.append(RenkoBrick("up", last_price, novo))

                last_price = novo

                count += 1

                if count > self.MAX_BRICKS_PER_TICK:
                    break

            count = 0

            while last_price - price >= self.brick_size:

                novo = last_price - self.brick_size

                bricks.append(RenkoBrick("down", last_price, novo))

                last_price = novo

                count += 1

                if count > self.MAX_BRICKS_PER_TICK:
                    break

        # -----------------------------------------
        # Brick em formação
        # -----------------------------------------

        ultimo_preco = float(ticks[-1]["last"])

        diferenca = ultimo_preco - last_price

        em_formacao = None

        if abs(diferenca) < self.brick_size and abs(diferenca) > 0:

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
