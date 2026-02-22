# mtcli-renko

Renko institucional para MetaTrader 5 integrado ao ecossistema `mtcli`.

Geração de gráfico Renko em modo texto (terminal), com:

- Renko simples
- Renko clássico (reversão 2x)
- Ancoragem real no último pregão
- Controle de barras por sessão
- Compatível com B3, Forex e ativos 24h
- Ideal para uso via CLI e automação

---

## Instalação

Via pip:

```bash
pip install mtcli-renko
````

Ou via Poetry:

```bash
poetry add mtcli-renko
```

---

## Requisitos

* Python 3.10+
* MetaTrader 5 instalado
* Conta conectada ao terminal MT5
* Plugin `mtcli` configurado

---

## Uso

Após instalar, o comando fica disponível dentro do `mt`:

```bash
mt renko --symbol WINJ26 --brick 50
```

---

## Parâmetros

| Opção                | Descrição                         |
| -------------------- | --------------------------------- |
| `--symbol`, `-s`     | Ativo (ex: WINJ26)                |
| `--brick`, `-b`      | Tamanho do brick                  |
| `--timeframe`, `-t`  | Timeframe (m1, m5, m15, h1, etc.) |
| `--bars`, `-n`       | Quantidade de barras base         |
| `--modo`             | `simples` ou `classico`           |
| `--ancorar-abertura` | Ancora no último pregão           |

---

## Exemplos

### Renko simples padrão

```bash
mt renko -s WINJ26 -b 50
```

### Renko clássico (reversão 2x)

```bash
mt renko -s WINJ26 -b 50 --modo classico
```

### Ancorado no último pregão

```bash
mt renko -s WINJ26 -b 50 --ancorar-abertura
```

### Todas as barras do último pregão

```bash
mt renko -s WINJ26 -b 50 --ancorar-abertura --bars 0
```

### Últimas 20 barras do último pregão

```bash
mt renko -s WINJ26 -b 50 --ancorar-abertura --bars 20
```

---

## Timeframes aceitos

Use valores simplificados:

* m1
* m5
* m15
* m30
* h1
* h4
* d1

O sistema faz o mapeamento automático para as constantes do MetaTrader 5.

---

## Ancoragem Institucional

Quando `--ancorar-abertura` é ativado:

* Detecta o último candle disponível
* Descobre a data do último pregão real
* Filtra manualmente apenas aquele dia
* Ignora histórico anterior
* Funciona inclusive em domingos e feriados

Comportamento:

* `--bars 0` → todas as barras do último pregão
* `--bars N` → últimas N barras daquele pregão

---

## Modos de Construção

### Simples

Cria bricks contínuos sem regra de reversão 2x.

### Clássico

Implementa reversão apenas quando o preço move 2x o tamanho do brick na direção oposta.

---

## Estrutura do Projeto

```
mtcli_renko/
│
├── commands/
├── controllers/
├── models/
├── views/
├── conf.py
└── enums.py
```

Arquitetura baseada em MVC, alinhada ao padrão do `mtcli-trade`.

---

## Casos de Uso

* Leitura de estrutura (H1, H2, H3, L1, L2)
* Identificação de BRF / BLF
* Automação de análise
* Backtesting via script
* Operação institucional via terminal

---

## Compatibilidade

* B3 (ex: WIN, WDO)
* Forex
* Cripto
* Ativos 24h

---

## Roadmap

* [ ] Múltiplas sessões
* [ ] Filtro de horário (09:00–18:00)
* [ ] VWAP integrada
* [ ] Detecção automática de estrutura (H1/H2/L2)
* [ ] Exportação CSV

---

## Licença

MIT License

---

## Autor

Valmir França

---

## Contribuição

Pull requests são bem-vindos.
Para mudanças maiores, abra uma issue antes para discussão.

---

## Aviso

Este software não constitui recomendação de investimento.
Uso por conta e risco do operador.
