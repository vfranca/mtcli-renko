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
        """
        Inicializa o modelo Renko.

        :param symbol: ativo (ex: WINJ26)
        :param brick_size: tamanho do bloco em pontos
        """
        self.symbol = symbol
        self.brick_size = brick_size

    def obter_rates(self, timeframe, quantidade: int):
        """
        Busca candles via copy_rates_from_pos usando contexto seguro MT5.

        :param timeframe: timeframe MT5
        :param quantidade: número de candles
        :return: numpy.ndarray ou None
        """
        log.info(
            f"[Renko] Solicitando {quantidade} candles de "
            f"{self.symbol} no timeframe {timeframe}"
        )

        with mt5_conexao():

            # Garante que o símbolo está habilitado
            if not mt5.symbol_select(self.symbol, True):
                erro = mt5.last_error()
                log.error(
                    f"[Renko] Falha ao selecionar símbolo "
                    f"{self.symbol}: {erro}"
                )
                raise RuntimeError(
                    f"Não foi possível selecionar o símbolo {self.symbol}"
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

    def construir_renko(self, rates) -> List[RenkoBrick]:
        """
        Constrói blocos Renko baseados em HIGH/LOW para maior precisão.

        :param rates: numpy.ndarray estruturado retornado pelo MT5
        :return: lista de RenkoBrick
        """
        bricks: List[RenkoBrick] = []

        # IMPORTANTE: rates é numpy.ndarray → não usar "if not rates"
        if rates is None:
            log.error("[Renko] Rates é None.")
            return bricks

        if len(rates) < 2:
            log.warning("[Renko] Histórico insuficiente para gerar Renko.")
            return bricks

        last_price = float(rates[0]["close"])

        log.info(
            f"[Renko] Iniciando construção | "
            f"brick_size={self.brick_size} | "
            f"preço inicial={last_price}"
        )

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            # Movimento para cima
            while high - last_price >= self.brick_size:
                novo_close = last_price + self.brick_size

                bricks.append(
                    RenkoBrick("up", last_price, novo_close)
                )

                last_price = novo_close

            # Movimento para baixo
            while last_price - low >= self.brick_size:
                novo_close = last_price - self.brick_size

                bricks.append(
                    RenkoBrick("down", last_price, novo_close)
                )

                last_price = novo_close

        log.info(f"[Renko] Total de blocos gerados: {len(bricks)}")

        if not bricks:
            log.warning(
                "[Renko] Nenhum bloco gerado. "
                "Possível brick_size alto ou mercado lateral."
            )

        return bricks
