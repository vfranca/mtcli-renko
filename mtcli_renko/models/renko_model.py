"""
Renko model.

Responsável por:
- Buscar dados no MT5
- Construir os blocos Renko
"""

from dataclasses import dataclass
import MetaTrader5 as mt5


@dataclass
class RenkoBrick:
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
        """
        Busca candles via copy_rates_from_pos.

        :param timeframe: timeframe MT5
        :param quantidade: número de candles
        :return: lista de rates
        """
        return mt5.copy_rates_from_pos(self.symbol, timeframe, 0, quantidade)

    def construir_renko(self, rates):
        """
        Constrói blocos Renko baseados no fechamento dos candles.

        :param rates: dados OHLC
        :return: lista de RenkoBrick
        """
        bricks = []

        if not rates:
            return bricks

        last_price = rates[0]["close"]

        for rate in rates[1:]:
            price = rate["close"]

            while price - last_price >= self.brick_size:
                bricks.append(
                    RenkoBrick("up", last_price, last_price + self.brick_size)
                )
                last_price += self.brick_size

            while last_price - price >= self.brick_size:
                bricks.append(
                    RenkoBrick("down", last_price, last_price - self.brick_size)
                )
                last_price -= self.brick_size

        return bricks
