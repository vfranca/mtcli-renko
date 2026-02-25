"""
Renko controller.

Responsável por:
- Orquestrar obtenção de dados (candle ou tick)
- Chamar o model
- Aplicar estilo de saída no modo tick
"""

from ..models.renko_model import RenkoModel
from mtcli.logger import setup_logger

log = setup_logger(__name__)


class RenkoController:
    """
    Controller principal do Renko.

    :param symbol: ativo (ex: WINJ26)
    :param brick_size: tamanho do brick
    :param timeframe: timeframe MT5 (para candle)
    :param quantidade: número de candles
    :param modo: simples ou classico
    :param ancorar_abertura: ancora na abertura da sessão
    :param data_mode: candle ou tick
    :param max_ticks: quantidade máxima de ticks
    :param tick_style: estrutural | hibrido | agressivo
    """

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
        tick_style="hibrido",
    ):
        self.model = RenkoModel(symbol, brick_size)
        self.timeframe = timeframe
        self.quantidade = quantidade
        self.modo = modo
        self.ancorar_abertura = ancorar_abertura
        self.data_mode = data_mode
        self.max_ticks = max_ticks
        self.tick_style = tick_style

    def executar(self):
        """
        Executa construção do Renko conforme modo configurado.
        """

        # =========================
        # MODO TICK
        # =========================
        if self.data_mode == "tick":

            ticks = self.model.obter_ticks(
                timeframe=self.timeframe,
                max_ticks=self.max_ticks,
            )

            # 🔒 Correção definitiva do erro numpy
            if ticks is None or len(ticks) == 0:
                return []

            resultado = self.model.construir_renko_ticks(ticks)

            # =========================
            # Aplicar estilo de tick
            # =========================

            # Estrutural → somente confirmados
            if self.tick_style == "estrutural":
                return resultado.confirmados

            # Agressivo → confirmados + parcial como válido
            if self.tick_style == "agressivo":
                if resultado.em_formacao:
                    return resultado.confirmados + [resultado.em_formacao]
                return resultado.confirmados

            # Híbrido (default) → retorna objeto completo
            return resultado

        # =========================
        # MODO CANDLE
        # =========================
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
