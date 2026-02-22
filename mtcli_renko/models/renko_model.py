"""
Renko model institucional.

Ancoragem determinística no último pregão real.
Nunca depende do filtro interno do MT5.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

import MetaTrader5 as mt5

from mtcli.mt5_context import mt5_conexao
from mtcli.logger import setup_logger

log = setup_logger(__name__)


# ==========================================================
# DATA STRUCTURE
# ==========================================================

@dataclass
class RenkoBrick:
    direction: str
    open: float
    close: float


# ==========================================================
# MODEL
# ==========================================================

class RenkoModel:

    def __init__(self, symbol: str, brick_size: float):
        self.symbol = symbol
        self.brick_size = brick_size

    # ======================================================
    # OBTENÇÃO DE DADOS
    # ======================================================

    def obter_rates(self, timeframe, quantidade: int, ancorar_abertura=False):

        with mt5_conexao():

            if not mt5.symbol_select(self.symbol, True):
                raise RuntimeError(f"Erro ao selecionar símbolo {self.symbol}")

            # -------------------------------------------------
            # SEM ANCORAGEM
            # -------------------------------------------------
            if not ancorar_abertura:

                if quantidade == 0:
                    quantidade = 1000

                return mt5.copy_rates_from_pos(
                    self.symbol,
                    timeframe,
                    0,
                    quantidade,
                )

            # -------------------------------------------------
            # COM ANCORAGEM PROFISSIONAL
            # -------------------------------------------------

            # 1️⃣ Descobrir último candle real disponível
            ultimo = mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                1,
            )

            if ultimo is None or len(ultimo) == 0:
                return None

            ultimo_time = datetime.fromtimestamp(ultimo[0]["time"])
            data_referencia = ultimo_time.date()

            log.info(f"[Renko] Último pregão detectado: {data_referencia}")

            # 2️⃣ Buscar bloco recente grande
            bruto = mt5.copy_rates_from_pos(
                self.symbol,
                timeframe,
                0,
                5000,
            )

            if bruto is None:
                return None

            # 3️⃣ FILTRAGEM MANUAL POR DATA
            filtrado = []

            for r in bruto:
                r_time = datetime.fromtimestamp(r["time"])
                if r_time.date() == data_referencia:
                    filtrado.append(r)

            if not filtrado:
                return None

            total = len(filtrado)

            log.info(f"[Renko] Barras no último pregão: {total}")

            # 4️⃣ Aplicar regra de quantidade
            if quantidade == 0:
                return filtrado

            if quantidade >= total:
                return filtrado

            return filtrado[-quantidade:]

    # ======================================================
    # CONSTRUÇÃO RENKO
    # ======================================================

    def construir_renko(
        self,
        rates,
        modo="simples",
        ancorar_abertura=False,
    ) -> List[RenkoBrick]:

        if not rates or len(rates) < 2:
            return []

        if modo == "classico":
            return self._construir_classico(rates, ancorar_abertura)

        return self._construir_simples(rates, ancorar_abertura)

    # ======================================================
    # RENKO SIMPLES
    # ======================================================

    def _construir_simples(self, rates, ancorar_abertura):

        bricks: List[RenkoBrick] = []

        last_price = float(rates[0]["open"]) if ancorar_abertura else float(
            rates[0]["close"]
        )

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            # Up bricks
            while high - last_price >= self.brick_size:
                novo = last_price + self.brick_size
                bricks.append(RenkoBrick("up", last_price, novo))
                last_price = novo

            # Down bricks
            while last_price - low >= self.brick_size:
                novo = last_price - self.brick_size
                bricks.append(RenkoBrick("down", last_price, novo))
                last_price = novo

        return bricks

    # ======================================================
    # RENKO CLÁSSICO (REVERSÃO 2x)
    # ======================================================

    def _construir_classico(self, rates, ancorar_abertura):

        bricks: List[RenkoBrick] = []

        last_price = float(rates[0]["open"]) if ancorar_abertura else float(
            rates[0]["close"]
        )

        direction: Optional[str] = None

        for rate in rates[1:]:

            high = float(rate["high"])
            low = float(rate["low"])

            # -------------------------------------------------
            # Continuação de alta
            # -------------------------------------------------
            if direction in (None, "up"):

                while high - last_price >= self.brick_size:
                    novo = last_price + self.brick_size
                    bricks.append(RenkoBrick("up", last_price, novo))
                    last_price = novo
                    direction = "up"

                # reversão 2x
                if direction == "up" and last_price - low >= 2 * self.brick_size:
                    novo = last_price - self.brick_size
                    bricks.append(RenkoBrick("down", last_price, novo))
                    last_price = novo
                    direction = "down"

            # -------------------------------------------------
            # Continuação de baixa
            # -------------------------------------------------
            if direction in (None, "down"):

                while last_price - low >= self.brick_size:
                    novo = last_price - self.brick_size
                    bricks.append(RenkoBrick("down", last_price, novo))
                    last_price = novo
                    direction = "down"

                # reversão 2x
                if direction == "down" and high - last_price >= 2 * self.brick_size:
                    novo = last_price + self.brick_size
                    bricks.append(RenkoBrick("up", last_price, novo))
                    last_price = novo
                    direction = "up"

        return bricks
