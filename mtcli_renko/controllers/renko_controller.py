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

    Parameters
    ----------
    symbol : str
        Ativo (ex: WINJ26)

    brick_size : float
        Tamanho do brick

    timeframe : int
        Timeframe MT5

    quantidade : int
        Número de candles

    modo : str
        simples | classico

    ancorar_abertura : bool
        Ancora sessão na abertura

    data_mode : str
        candle | tick

    max_ticks : int
        Número máximo de ticks utilizados

    tick_style : str
        estrutural | hibrido | agressivo

    price_min : float
        Filtro mínimo de preço

    price_max : float
        Filtro máximo de preço

    limit_bricks : int
        Limite de blocos retornados

    reverse : bool
        Inverte ordem dos blocos
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

        self.symbol = symbol
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
        """
        Executa o cálculo do Renko.

        Returns
        -------
        list | RenkoTickResult
        """

        # ======================================================
        # TICK MODE
        # ======================================================

        if self.data_mode == "tick":

            log.info(
                "Renko TICK | symbol=%s max_ticks=%s ancorar_abertura=%s",
                self.symbol,
                self.max_ticks,
                self.ancorar_abertura,
            )

            ticks = self.model.obter_ticks(
                max_ticks=self.max_ticks,
                ancorar_abertura=self.ancorar_abertura,
            )

            if not ticks:
                log.warning("Nenhum tick encontrado no banco.")
                return []

            log.debug("Ticks carregados: %s", len(ticks))

            resultado = self.model.construir_renko_ticks(
                ticks,
                modo=self.modo,
            )

            bricks = list(resultado.confirmados)

        # ======================================================
        # CANDLE MODE
        # ======================================================

        else:

            log.info(
                "Renko CANDLE | symbol=%s timeframe=%s bars=%s ancorar_abertura=%s",
                self.symbol,
                self.timeframe,
                self.quantidade,
                self.ancorar_abertura,
            )

            rates = self.model.obter_rates(
                self.timeframe,
                self.quantidade,
                ancorar_abertura=self.ancorar_abertura,
            )

            if not rates:
                log.warning("Nenhum candle retornado.")
                return []

            log.debug("Candles carregados: %s", len(rates))

            bricks = self.model.construir_renko(
                rates,
                modo=self.modo,
            )

            resultado = bricks

        # ======================================================
        # FILTROS
        # ======================================================

        if self.price_min is not None:

            log.debug("Aplicando filtro price_min=%s", self.price_min)

            bricks = [
                b for b in bricks
                if b.close >= self.price_min
            ]

        if self.price_max is not None:

            log.debug("Aplicando filtro price_max=%s", self.price_max)

            bricks = [
                b for b in bricks
                if b.close <= self.price_max
            ]

        if self.reverse:

            log.debug("Invertendo ordem dos bricks")

            bricks = list(reversed(bricks))

        if self.limit_bricks:

            log.debug("Limitando bricks a %s", self.limit_bricks)

            bricks = bricks[-self.limit_bricks:]

        # ======================================================
        # TICK STYLE
        # ======================================================

        if self.data_mode == "tick":

            # ----------------------------------------------
            # estrutural → apenas confirmados
            # ----------------------------------------------

            if self.tick_style == "estrutural":

                log.debug("Tick style: estrutural")

                return bricks

            # ----------------------------------------------
            # agressivo → inclui bloco em formação
            # ----------------------------------------------

            if self.tick_style == "agressivo":

                log.debug("Tick style: agressivo")

                if resultado.em_formacao:
                    bricks.append(resultado.em_formacao)

                return bricks

            # ----------------------------------------------
            # híbrido → confirmados + formação separado
            # ----------------------------------------------

            log.debug("Tick style: hibrido")

            resultado = resultado._replace(confirmados=bricks)

            return resultado

        return bricks
