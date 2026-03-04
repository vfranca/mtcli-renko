"""
Configurações do plugin mtcli-renko.

Este módulo centraliza o carregamento das configurações utilizadas pelo
plugin Renko a partir do arquivo de configuração do mtcli (mtcli.ini).

As configurações são lidas através do sistema de configuração global
do mtcli:

    from mtcli.conf import conf

Cada parâmetro é obtido da seção:

    [renko]

Caso a configuração não exista no arquivo de configuração do usuário,
um valor padrão seguro é utilizado.

Exemplo de configuração no mtcli.ini:

    [renko]

    symbol = WIN$N
    digits = 0
    period = m1
    data_mode = tick
    bars = 500
    brick = 60
    max_ticks = 500000
    tick_style = hibrido
    modo = simples
    limit_bricks = 200
    session_open = 09:00
    session_open_offset_seconds = -47
    ancorar_abertura = true

Essas configurações controlam:

 fonte de dados (tick ou candle)
 tamanho do bloco Renko
 modo de construção
 comportamento da ancoragem na abertura do pregão
"""

from mtcli.conf import conf


# ==========================================================
# SEÇÃO DE CONFIGURAÇÃO
# ==========================================================

"""
Seção `[renko]` do arquivo mtcli.ini.

Todas as configurações deste plugin são carregadas a partir desta seção.
"""
renko = conf.section("renko")


# ==========================================================
# ATIVO
# ==========================================================

"""
Símbolo utilizado para construção do Renko.

Exemplo:
    WIN$N
    WDO$N
    PETR4
"""
SYMBOL = renko.get("symbol", default="WIN$N")


# ==========================================================
# FORMATAÇÃO DE PREÇO
# ==========================================================

"""
Número de dígitos após o ponto decimal utilizados na exibição
dos preços.

Exemplo:

    0  →  123456
    2  →  1234.56
"""
DIGITS = renko.get("digits", cast=int, default=0)


# ==========================================================
# TIMEFRAME BASE (MODO CANDLE)
# ==========================================================

"""
Timeframe utilizado para obter candles quando o modo de dados
é configurado como `candle`.

Exemplos comuns:

    m1
    m5
    m15
"""
PERIOD = renko.get("period", default="m1")


# ==========================================================
# MODO DE DADOS
# ==========================================================

"""
Fonte de dados utilizada para construção do Renko.

Valores possíveis:

    tick   -  usa ticks individuais (mais preciso)
    candle  - usa candles OHLC

O modo tick permite reconstrução mais fiel da sequência
de movimentos do preço.
"""
DATA_MODE = renko.get("data_mode", default="tick")


# ==========================================================
# QUANTIDADE DE CANDLES
# ==========================================================

"""
Quantidade de candles carregados quando DATA_MODE=candle.

Valores maiores permitem reconstrução mais longa do histórico
de blocos Renko.
"""
BARS = renko.get("bars", cast=int, default=566)


# ==========================================================
# TAMANHO DO BLOCO RENKO
# ==========================================================

"""
Tamanho do bloco Renko.

Exemplo:

    60 - bloco de 60 pontos
"""
BRICK = renko.get("brick", cast=float, default=60)


# ==========================================================
# LIMITE DE TICKS
# ==========================================================

"""
Quantidade máxima de ticks utilizados na reconstrução
do Renko no modo tick.

Valores grandes permitem reconstrução profunda,
mas aumentam consumo de memória e CPU.
"""
MAX_TICKS = renko.get("max_ticks", cast=int, default=5000000)


# ==========================================================
# ESTILO RENKO BASEADO EM TICKS
# ==========================================================

"""
Define o estilo de reconstrução Renko quando DATA_MODE=tick.

Valores possíveis:

    estrutural
    agressivo
    hibrido

O modo híbrido normalmente produz melhor equilíbrio entre
sensibilidade e estabilidade estrutural.
"""
TICK_STYLE = renko.get("tick_style", default="hibrido")


# ==========================================================
# MODO RENKO
# ==========================================================

"""
Algoritmo de construção dos blocos Renko.

Valores possíveis:

    simples
    classico

Dependendo da estratégia, o modo clássico pode exigir
movimento adicional para reversão.
"""
MODO = renko.get("modo", default="simples")


# ==========================================================
# LIMITE DE BLOCOS EXIBIDOS
# ==========================================================

"""
Quantidade máxima de blocos Renko exibidos no terminal.

Valores:

    0 - exibe todos os blocos
"""
LIMIT_BRICKS = renko.get("limit_bricks", cast=int, default=0)


# ==========================================================
# ABERTURA DO PREGÃO
# ==========================================================

"""
Hora oficial de abertura da sessão de negociação.

Formato:

    HH:MM

Exemplo:

    09:00
"""
SESSION_OPEN = renko.get("session_open", default="09:00")


# ==========================================================
# OFFSET DE SEGUNDOS DA ABERTURA
# ==========================================================

"""
Offset aplicado ao horário de abertura do pregão.

Usado para compensar diferenças entre:

horário da corretora (UTC)
horário local da bolsa (B3)

Exemplo:

    -47  → ignora primeiros 47 segundos da sessão
"""
SESSION_OPEN_OFFSET_SECONDS = renko.get(
    "session_open_offset_seconds",
    cast=int,
    default=0,
)


# ==========================================================
# OFFSET UTC DA CORRETORA
# ==========================================================

"""
Diferença entre o horário do servidor da corretora e o horário UTC.

Algumas corretoras fornecem timestamps em UTC puro enquanto
outras utilizam horário local do servidor.

Este parâmetro permite ajustar essa diferença para que cálculos
baseados em horário (como a ancoragem na abertura do pregão)
sejam feitos corretamente.

Exemplo para a B3:

    broker_utc_offset = -3

Isso significa que o horário da bolsa está **3 horas atrás do UTC**.

Exemplo prático:

    UTC           - 12:00
    B3 (offset -3) - 09:00

Esse valor é utilizado principalmente nos cálculos de:

`SESSION_OPEN`
filtragem de ticks da sessão
reconstrução de Renko ancorado na abertura
"""
BROKER_UTC_OFFSET = renko.get("broker_utc_offset", cast=int, default=-3)
