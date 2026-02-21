"""
Renko model.

Responsável por:
- Gerenciar conexão com MT5
- Buscar dados históricos
- Construir blocos Renko
"""

from dataclasses import dataclass
from typing import List, Optional

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger

log = setup_logger(__name__)


@dataclass
class RenkoBrick:
    """
    Representa um bloco Renko.
    """

    direction: str  # "up" ou "down"
    open: float
    close: float


class RenkoModel:
    """
    Modelo responsável pela geração de blocos Renko.
    """

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size

    def obter_rates(self, timeframe, quantidade: int):

        log.info(
            f"[Renko] Solicitando {quantidade} candles de "
            f"{self.symbol} no timeframe {timeframe}"
        )

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                erro = mt5.last_error()
                raise RuntimeError(
                    f"Não foi possível selecionar o símbolo {self.symbol}: {erro}"
                )

            rates = mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                quantidade,
            )

            if rates is None:
                erro = mt5.last_error()
                log.error(f"[Renko] copy_rates retornou None: {erro}")
                return None

            log.info(f"[Renko] {len(rates)} candles recebidos do MT5")

            return rates

    def construir_renko(self, rates, modo="simples") -> List[RenkoBrick]:

        if modo == "classico":
            return self._construir_renko_classico(rates)

        return self._construir_renko_simples(rates)

    # -----------------------------
    # MODO SIMPLES
    # -----------------------------

    def _construir_renko_simples(self, rates) -> List[RenkoBrick]:

        bricks: List[RenkoBrick] = []

        if rates is None or len(rates) < 2:
            return bricks

        last_price = float(rates[0]["close"])

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            while high - last_price >= self.brick_size:
                novo_close = last_price + self.brick_size
                bricks.append(RenkoBrick("up", last_price, novo_close))
                last_price = novo_close

            while last_price - low >= self.brick_size:
                novo_close = last_price - self.brick_size
                bricks.append(RenkoBrick("down", last_price, novo_close))
                last_price = novo_close

        log.info(f"[Renko Simples] Total de blocos: {len(bricks)}")
        return bricks

    # -----------------------------
    # MODO CLÁSSICO (REVERSÃO 2x)
    # -----------------------------

    def _construir_renko_classico(self, rates) -> List[RenkoBrick]:

        bricks: List[RenkoBrick] = []

        if rates is None or len(rates) < 2:
            return bricks

        last_price = float(rates[0]["close"])
        direction: Optional[str] = None

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            # CONTINUAÇÃO DE ALTA
            if direction in (None, "up"):

                while high - last_price >= self.brick_size:
                    novo_close = last_price + self.brick_size
                    bricks.append(RenkoBrick("up", last_price, novo_close))
                    last_price = novo_close
                    direction = "up"

                if direction == "up" and last_price - low >= 2 * self.brick_size:
                    novo_close = last_price - self.brick_size
                    bricks.append(RenkoBrick("down", last_price, novo_close))
                    last_price = novo_close
                    direction = "down"

            # CONTINUAÇÃO DE BAIXA
            if direction in (None, "down"):

                while last_price - low >= self.brick_size:
                    novo_close = last_price - self.brick_size
                    bricks.append(RenkoBrick("down", last_price, novo_close))
                    last_price = novo_close
                    direction = "down"

                if direction == "down" and high - last_price >= 2 * self.brick_size:
                    novo_close = last_price + self.brick_size
                    bricks.append(RenkoBrick("up", last_price, novo_close))
                    last_price = novo_close
                    direction = "up"

        log.info(f"[Renko Classico] Total de blocos: {len(bricks)}")
        return bricks
