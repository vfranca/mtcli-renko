"""
Renko controller.
"""

from ..models.renko_model import RenkoModel
from mtcli.logger import setup_logger

log = setup_logger(__name__)


class RenkoController:

    def __init__(
        self,
        symbol,
        brick_size,
        timeframe,
        quantidade,
        modo="simples",
        ancorar_abertura=False,
        data_mode="candle",
        max_ticks=3000,
    ):
        self.model = RenkoModel(symbol, brick_size)
        self.timeframe = timeframe
        self.quantidade = quantidade
        self.modo = modo
        self.ancorar_abertura = ancorar_abertura
        self.data_mode = data_mode
        self.max_ticks = max_ticks

    def executar(self):

        # -------------------------------------------------
        # TICK MODE
        # -------------------------------------------------

        if self.data_mode == "tick":

            ticks = self.model.obter_ticks(
                timeframe=self.timeframe,
                max_ticks=self.max_ticks,
            )

            if ticks is None or len(ticks) == 0:
                return []

            return self.model.construir_renko_ticks(ticks)

        # -------------------------------------------------
        # CANDLE MODE
        # -------------------------------------------------

        rates = self.model.obter_rates(
            self.timeframe,
            self.quantidade,
            ancorar_abertura=self.ancorar_abertura,
        )

        if rates is None or len(rates) == 0:
            return []

        return self.model.construir_renko(
            rates,
            modo=self.modo,
        )
