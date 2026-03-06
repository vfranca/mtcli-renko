# mtcli-renko

Plugin **Renko profissional para o mtcli**.

O **mtcli-renko** adiciona ao CLI `mt` a capacidade de gerar **blocos Renko diretamente no terminal**, utilizando dados do **MetaTrader 5** ou de outras fontes configuradas no `mtcli`.

O plugin foi projetado para **análise de fluxo e price action**, oferecendo geração de Renko baseada em **ticks ou candles**, múltiplos **estilos de cálculo**, e saída **acessível para ambientes CLI**.

---

# Características

* geração de **Renko a partir de ticks**
* geração de **Renko a partir de candles**
* **modo candle determinístico**
* **modo tick híbrido** (blocos confirmados + bloco em formação)
* **reconstrução do caminho do candle (path reconstruction)**
* **ancoragem opcional na abertura do pregão**
* ajuste automático de **UTC do servidor da corretora**
* **margem de segurança na abertura do pregão**
* saída em **texto puro**, ideal para terminal e leitores de tela
* arquitetura **MVC modular**

---

# Requisitos

* Python **3.10+**
* **MetaTrader 5**
* **mtcli**

Projeto relacionado:

[https://github.com/vfranca/mtcli](https://github.com/vfranca/mtcli)

---

# Instalação

Via pip:

```bash
pip install mtcli-renko
```

Ou com poetry:

```bash
poetry add mtcli-renko
```

Após a instalação o plugin será automaticamente carregado pelo **mtcli**.

---

# Comando

O plugin adiciona o comando:

```
mt rk
```

Exemplo simples:

```bash
mt rk
```

Exemplo com parâmetros:

```bash
mt rk --brick 60
```

---

# Exemplo de saída

```
=== GRAFICO RENKO ===
Total de blocos: 5

METRICAS:
Up: 2
Down: 3
Delta: -1

PADROES:
H1

DOWN 181915 181855
UP 181855 181915
DOWN 181915 181855
DOWN 181855 181795
UP 181795 181855
```

Quando o **modo tick híbrido** está ativo, o último bloco pode aparecer como **em formação**.

---

# Modos de geração

O plugin suporta dois modos principais de dados.

## Tick mode

Os blocos Renko são gerados diretamente a partir de **ticks do mercado**.

Vantagens:

* maior precisão
* captura movimentos intra-candle
* ideal para análise de fluxo

Disponibiliza três estilos:

```
estrutural
agressivo
hibrido
```

### Híbrido

Modo recomendado.

Exibe:

* blocos **confirmados**
* último bloco **em formação**

---

## Candle mode

Os blocos Renko são gerados a partir de **candles históricos**.

Características:

* cálculo **determinístico**
* reconstrução do caminho interno do candle
* resultados consistentes entre execuções

---

# Configuração

As configurações são definidas em:

```
mtcli.ini
```

Seção:

```
[renko]
```

Exemplo completo:

```
[renko]

symbol = WIN$N
digits = 0

period = m1
data_mode = tick

bars = 566

brick = 60

max_ticks = 5000000

tick_style = hibrido

modo = simples

limit_bricks = 0

session_open = 09:00

session_open_offset_seconds = 0

broker_utc_offset = -3
```

---

# Parâmetros

## symbol

Ativo utilizado para gerar o Renko.

Exemplo:

```
symbol = WIN$N
```

---

## digits

Número de casas decimais do ativo.

Exemplo:

```
digits = 0
```

---

## period

Timeframe utilizado quando:

```
data_mode = candle
```

Exemplo:

```
period = m1
```

---

## data_mode

Define a fonte de dados utilizada.

Valores possíveis:

```
tick
candle
```

---

## bars

Quantidade de candles carregados quando:

```
data_mode = candle
```

---

## brick

Tamanho do bloco Renko.

Exemplo:

```
brick = 60
```

---

## max_ticks

Número máximo de ticks carregados quando:

```
data_mode = tick
```

Isso evita consumo excessivo de memória.

---

## tick_style

Define o estilo de cálculo no modo **tick**.

Valores possíveis:

```
estrutural
agressivo
hibrido
```

### estrutural

Renko mais conservador.

### agressivo

Gera blocos mais rapidamente.

### híbrido

Combina estabilidade e reatividade e permite mostrar:

* blocos confirmados
* bloco em formação

---

## modo

Define o algoritmo base de cálculo.

Valores possíveis:

```
simples
classico
```

---

## limit_bricks

Limita a quantidade de blocos exibidos.

Exemplo:

```
limit_bricks = 200
```

---

## session_open

Hora oficial de abertura do pregão.

Formato:

```
HH:MM
```

Exemplo:

```
session_open = 09:00
```

---

## session_open_offset_seconds

Margem de segurança aplicada à abertura do pregão.

Algumas corretoras enviam os primeiros ticks **alguns segundos após a abertura oficial**.

Esse parâmetro evita problemas de ancoragem.

Exemplo:

```
session_open_offset_seconds = 47
```

---

## broker_utc_offset

Offset UTC do servidor da corretora.

Exemplo:

```
broker_utc_offset = -3
```

---

# Exemplos de uso

## Renko padrão

```
mt rk
```

---

## Definir tamanho do brick

```
mt rk --brick 30
```

---

## Limitar quantidade de blocos

```
mt rk --limit-bricks 200
```

---

## Usar modo candle

```
mt rk --data-mode candle
```

---

# Arquitetura

O plugin segue arquitetura **MVC**, separando responsabilidades:

```
mtcli_renko/

commands/
    renko.py

controllers/
    renko_controller.py

models/
    renko_model.py

views/
    renko_view.py

conf.py
plugin.py
```

### Model

Responsável por:

* geração dos blocos Renko
* cálculo dos algoritmos
* reconstrução de path do candle
* lógica de tick e candle

### Controller

Responsável por:

* fluxo da execução
* carregamento de dados
* integração com o mtcli

### View

Responsável por:

* exibir os blocos no terminal
* saída compatível com leitores de tela
* formatação textual simples

---

# Desenvolvimento

Clone o repositório:

```
git clone https://github.com/vfranca/mtcli-renko
```

Instale dependências:

```
poetry install
```

---

# Testes

Execute:

```
pytest
```

---

# Licença

MIT License

---

# Autor

Valmir França
