"""
conf.py

Módulo de configuração do plugin mtcli-delta.

Responsável por:

- Ler configurações do arquivo mtcli.ini
- Utilizar a seção [RENKO]
- Permitir override por variáveis de ambiente
- Definir valores padrão seguros

Ordem de precedência:

1. Variáveis de ambiente
2. Seção [RENKO] do mtcli.ini
3. Seção [DEFAULT] do mtcli.ini
4. Valores padrão definidos no código
"""

import os
from mtcli.conf import config


def _get_config_value(section: str, key: str, fallback):
    """
    Obtém valor do arquivo de configuração com fallback seguro.

    Ordem:
    - Se existir na seção informada
    - Se existir em DEFAULT
    - Caso contrário usa fallback

    :param section: Nome da seção no ini.
    :param key: Nome da chave.
    :param fallback: Valor padrão final.
    :return: Valor encontrado ou fallback.
    """
    if config.has_section(section) and key in config[section]:
        return config[section].get(key, fallback=fallback)

    return config["DEFAULT"].get(key, fallback=fallback)


# -------------------------------------------------------
# Leitura da seção [RENKO] do mtcli.ini
# -------------------------------------------------------

SYMBOL = os.getenv(
    "SYMBOL",
    _get_config_value("RENKO", "symbol", "WIN$N")
)

BRICK = float(os.getenv(
    "BRICK",
    _get_config_value("RENKO", "brick", 50)
))

PERIOD = os.getenv(
    "PERIOD",
    _get_config_value("RENKO", "period", "M5")
)

BARS = int(os.getenv(
    "BARS",
    _get_config_value("RENKO", "bars", 500)
))

DIGITS = int(os.getenv(
    "DIGITS",
    _get_config_value("RENKO", "digits", 2)
))

# Hora oficial de abertura do pregão (HH:MM)
SESSION_OPEN = os.getenv(
    "SESSION_OPEN",
    _get_config_value("RENKO", "session_open", "09:00")
)

DATA_MODE = os.getenv(
    "DATA_MODE",
    _get_config_value("RENKO", "data_mode", "candle")
)

MAX_TICKS = int(os.getenv(
    "MAX_TICKS",
    _get_config_value("RENKO", "max_ticks", 10000)
))

TICK_STYLE = os.getenv(
    "TICK_STYLE",
    _get_config_value("RENKO", "tick_style", "hibrido")
)

