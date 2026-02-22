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
    ):
        self.model = RenkoModel(symbol, brick_size)
        self.timeframe = timeframe
        self.quantidade = quantidade
        self.modo = modo
        self.ancorar_abertura = ancorar_abertura

    def executar(self):

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
            ancorar_abertura=self.ancorar_abertura,
        )
