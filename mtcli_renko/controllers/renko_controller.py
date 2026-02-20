"""
Renko controller.
"""

from ..models.renko_model import RenkoModel


class RenkoController:
    """
    Orquestra a geração e exibição do Renko.
    """

    def __init__(self, symbol, brick_size, timeframe, quantidade):
        self.model = RenkoModel(symbol, brick_size)
        self.timeframe = timeframe
        self.quantidade = quantidade

    def executar(self):
        """
        Executa fluxo completo:
        - Busca dados
        - Gera blocos
        - Retorna estrutura pronta
        """
        rates = self.model.obter_rates(self.timeframe, self.quantidade)
        return self.model.construir_renko(rates)
