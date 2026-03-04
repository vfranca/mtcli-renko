# mtcli-renko

Plugin Renko para o **mtcli**.

O **mtcli-renko** adiciona ao CLI `mt` a capacidade de gerar **gráficos Renko diretamente no terminal**, utilizando dados do **MetaTrader 5** ou de outras fontes configuradas no `mtcli`.

O plugin suporta geração de Renko baseada em **ticks ou candles**, diferentes **estilos de cálculo**, e recursos úteis para análise de fluxo e price action.

---

# Características

* geração de **Renko a partir de ticks**
* geração de **Renko a partir de candles**
* suporte a **Renko estrutural, agressivo e híbrido**
* opção de **ancorar os blocos na abertura do pregão**
* compatível com **plugins e arquitetura modular do mtcli**
* saída em **texto puro**, ideal para terminal e leitores de tela

---

# Requisitos

* Python 3.10+
* MetaTrader 5 instalado
* mtcli instalado

Projeto relacionado:

* [https://github.com/mtcli/mtcli](https://github.com/mtcli/mtcli)

---

# Instalação

Instale via pip:

```bash
pip install mtcli-renko
```

ou usando poetry:

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

Exemplo:

```bash
mt rk
```

Também é possível informar parâmetros:

```bash
mt rk --brick 60
```

---

# Exemplo de saída

```
#   time                open    close
1   2026-01-10 09:01    128900  128960
2   2026-01-10 09:02    128960  129020
3   2026-01-10 09:04    129020  129080
```

---

# Configuração

As configurações podem ser definidas no arquivo:

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

ancorar_abertura = false
```

---

# Parâmetros

### symbol

Ativo utilizado para gerar o Renko.

Exemplo:

```
symbol = WIN$N
```

---

### digits

Número de casas decimais do ativo.

Exemplo:

```
digits = 0
```

---

### period

Timeframe usado quando o modo de dados é `candle`.

Exemplo:

```
period = m1
```

---

### data_mode

Define a fonte de dados utilizada.

Valores possíveis:

```
tick
candle
```

---

### bars

Quantidade de candles usados para cálculo no modo candle.

---

### brick

Tamanho do bloco Renko.

Exemplo:

```
brick = 60
```

---

### max_ticks

Limite máximo de ticks carregados quando `data_mode = tick`.

Isso evita consumo excessivo de memória.

---

### tick_style

Define o estilo de Renko baseado em ticks.

Valores possíveis:

```
estrutural
agressivo
hibrido
```

---

### modo

Modo de geração do Renko.

Valores possíveis:

```
simples
classico
```

---

### limit_bricks

Limita a quantidade de blocos exibidos.

Exemplo:

```
limit_bricks = 200
```

---

### session_open

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

### session_open_offset_seconds

Margem de segurança aplicada à abertura do pregão.

Isso ajuda a evitar problemas quando os primeiros ticks chegam alguns segundos após a abertura oficial.

Exemplo:

```
session_open_offset_seconds = 47
```

---

### broker_utc_offset

Offset UTC do servidor da corretora.

Exemplo:

```
broker_utc_offset = -3
```

---

### ancorar_abertura

Quando ativado, os blocos Renko são **ancorados na abertura do pregão**.

Exemplo:

```
ancorar_abertura = true
```

---

# Exemplos

### Renko padrão

```
mt rk
```

---

### Renko com brick diferente

```
mt rk --brick 30
```

---

### Limitar blocos exibidos

```
mt rk --limit-bricks 200
```

---

# Arquitetura

O plugin segue arquitetura MVC:

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

Essa estrutura facilita:

* manutenção
* testes automatizados
* evolução do plugin

---

# Desenvolvimento

Clone o repositório:

```
git clone https://github.com/mtcli/mtcli-renko
```

Instale em modo desenvolvimento:

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

