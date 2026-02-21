"""
Renko controller.
"""

from ..models.renko_model import RenkoModel
from mtcli.logger import setup_logger

log = setup_logger(__name__)


class RenkoController:
    """
    Orquestra a geração do Renko.
    """

    def __init__(self, symbol, brick_size, timeframe, quantidade, modo="simples"):
        self.model = RenkoModel(symbol, brick_size)
        self.timeframe = timeframe
        self.quantidade = quantidade
        self.modo = modo

    def executar(self):
        """
        Executa fluxo completo:
        - Busca dados
        - Gera blocos
        - Retorna estrutura pronta
        """

        log.info("[RenkoController] Iniciando execução do Renko.")

        rates = self.model.obter_rates(self.timeframe, self.quantidade)

        if rates is None:
            log.error("[RenkoController] Falha ao obter dados do MT5.")
            return []

        bricks = self.model.construir_renko(rates, modo=self.modo)

        log.info("[RenkoController] Execução finalizada.")

        return bricks
