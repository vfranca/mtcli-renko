"""
Renko controller.

Responsável por:

- Orquestrar obtenção de dados (candle ou tick)
- Chamar o model
- Aplicar filtros e estilos
"""

from ..models.renko_model import RenkoModel
from mtcli.logger import setup_logger

log = setup_logger(__name__)


class RenkoController:
    """
    Controller principal do Renko.

    :param symbol: ativo
    :param brick_size: tamanho do brick
    :param timeframe: timeframe MT5
    :param quantidade: número de candles
    :param modo: simples | classico
    :param ancorar_abertura: ancora sessão
    :param data_mode: candle | tick
    :param max_ticks: limite ticks
    :param tick_style: estrutural | hibrido | agressivo
    :param price_min: filtro preço mínimo
    :param price_max: filtro preço máximo
    :param limit_bricks: limite de blocos
    :param reverse: inverter ordem
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
        price_min=None,
        price_max=None,
        limit_bricks=None,
        reverse=False,
    ):

        self.model = RenkoModel(symbol, brick_size)

        self.timeframe = timeframe
        self.quantidade = quantidade
        self.modo = modo

        self.ancorar_abertura = ancorar_abertura
        self.data_mode = data_mode
        self.max_ticks = max_ticks
        self.tick_style = tick_style

        self.price_min = price_min
        self.price_max = price_max
        self.limit_bricks = limit_bricks
        self.reverse = reverse

    # ==========================================================
    # EXECUÇÃO
    # ==========================================================

    def executar(self):

        # ======================================================
        # TICK MODE
        # ======================================================

        if self.data_mode == "tick":

            ticks = self.model.obter_ticks(
                max_ticks=self.max_ticks,
                ancorar_abertura=self.ancorar_abertura,
            )

            if ticks is None or len(ticks) == 0:
                log.warning("Nenhum tick retornado.")
                return []

            resultado = self.model.construir_renko_ticks(ticks)

            bricks = resultado.confirmados

        # ======================================================
        # CANDLE MODE
        # ======================================================

        else:

            rates = self.model.obter_rates(
                self.timeframe,
                self.quantidade,
                ancorar_abertura=self.ancorar_abertura,
            )

            if rates is None or len(rates) == 0:
                log.warning("Nenhum candle retornado.")
                return []

            bricks = self.model.construir_renko(
                rates,
                modo=self.modo,
            )

            resultado = bricks

        # ======================================================
        # FILTROS
        # ======================================================

        if self.price_min is not None:
            bricks = [b for b in bricks if b.close >= self.price_min]

        if self.price_max is not None:
            bricks = [b for b in bricks if b.close <= self.price_max]

        if self.reverse:
            bricks = list(reversed(bricks))

        if self.limit_bricks:
            bricks = bricks[-self.limit_bricks:]

        # ======================================================
        # TICK STYLE
        # ======================================================

        if self.data_mode == "tick":

            if self.tick_style == "estrutural":
                return bricks

            if self.tick_style == "agressivo":

                if resultado.em_formacao:
                    bricks.append(resultado.em_formacao)

                return bricks

            # híbrido
            resultado = resultado._replace(confirmados=bricks)

            return resultado

        return bricks
