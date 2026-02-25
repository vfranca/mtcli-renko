"""
Renko controller.

Orquestra model e view.
Suporta:

✔ Candle mode (retorna lista de bricks)
✔ Tick mode híbrido (retorna RenkoResult)
"""

from ..models.renko_model import RenkoModel
from mtcli.logger import setup_logger

log = setup_logger(__name__)


class RenkoController:
    """
    Controlador responsável por:

    - Buscar dados (rates ou ticks)
    - Delegar construção ao model
    - Retornar estrutura adequada para a view
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
    ):
        """
        Inicializa o controller.

        :param symbol: ativo (ex: WINJ26)
        :param brick_size: tamanho do tijolo
        :param timeframe: constante MT5
        :param quantidade: número de candles
        :param modo: simples ou classico
        :param ancorar_abertura: usar apenas pregão atual (candle mode)
        :param data_mode: candle ou tick
        :param max_ticks: limite máximo de ticks processados
        """

        self.model = RenkoModel(symbol, brick_size)
        self.timeframe = timeframe
        self.quantidade = quantidade
        self.modo = modo
        self.ancorar_abertura = ancorar_abertura
        self.data_mode = data_mode
        self.max_ticks = max_ticks

    # ======================================================
    # EXECUÇÃO PRINCIPAL
    # ======================================================

    def executar(self):
        """
        Executa geração do Renko conforme modo selecionado.

        Retorna:
            - List[RenkoBrick] no candle mode
            - RenkoResult no tick mode híbrido
        """

        # -------------------------------------------------
        # TICK MODE (HÍBRIDO)
        # -------------------------------------------------

        if self.data_mode == "tick":

            ticks = self.model.obter_ticks(
                timeframe=self.timeframe,
                max_ticks=self.max_ticks,
            )

            if ticks is None or len(ticks) == 0:
                log.warning("Nenhum tick retornado.")
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
            log.warning("Nenhum rate retornado.")
            return []

        return self.model.construir_renko(
            rates,
            modo=self.modo,
        )
