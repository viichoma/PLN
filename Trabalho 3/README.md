# Agente de EDA em Linguagem Natural — COVID-19 Brasil.IO + DeepSeek

Projeto adaptado a partir do esqueleto `alex-marino/projeto_agente_eda` para analisar o arquivo `data/covid19.csv`, com dados de COVID-19 por município.

## O que este projeto faz

O usuário pergunta em português sobre o CSV. O agente consulta a API da DeepSeek, decide quais ferramentas Python deve chamar, executa cálculos reais em `pandas` e devolve uma resposta em linguagem natural.

Fluxo resumido:

```text
Usuário -> CLI -> Agent -> DeepSeek decide tool -> Tool pandas executa -> Agent devolve resultado -> DeepSeek responde
```

O LLM não executa código diretamente. Ele apenas pede chamadas de tools pré-registradas. Quem executa é o `Agent`, chamando funções Python controladas.

## Dataset

Arquivo usado: `data/covid19.csv`.

Colunas:

- `date`: data do boletim/registro mais recente disponível
- `state`: UF
- `city`: município
- `place_type`: tipo do local, neste recorte sempre `city`
- `confirmed`: casos confirmados acumulados
- `deaths`: óbitos acumulados
- `is_last`: flag de registro mais recente
- `estimated_population`: população estimada
- `city_ibge_code`: código IBGE
- `confirmed_per_100k_inhabitants`: casos por 100 mil habitantes
- `death_rate`: óbitos / casos confirmados

Resumo do arquivo enviado:

- 5.589 linhas
- 11 colunas
- 27 UFs
- 5.298 nomes distintos de municípios
- datas entre 2021-08-22 e 2022-03-26

## Instalação

```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows PowerShell
# .\venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
```

Edite o `.env`:

```env
DEEPSEEK_API_KEY=sk-sua-chave-aqui
LLM_MODEL=deepseek-v4-flash
DEEPSEEK_THINKING=disabled
```

## Execução interativa

```bash
python cli.py
```

Exemplos de perguntas:

```text
Quais são as colunas do dataset?
Qual estado tem mais casos confirmados no total?
Quais são os 5 municípios com mais óbitos?
Qual é a correlação entre confirmed e deaths?
Gere um gráfico de barras por estado.
```

Comandos da CLI:

```text
/ajuda       mostra comandos
/colunas     lista colunas sem chamar LLM
/trajetoria  mostra os passos e tools da última pergunta
/custo       mostra tokens e latência acumulados
/sair        encerra
```

## Rodar testes

```bash
pytest tests/ -v
```

## Rodar benchmark

Antes, confirme que a chave DeepSeek está no `.env`. Depois:

```bash
python -m evaluation.benchmark
```

O benchmark possui 30 perguntas:

- 10 factuais
- 15 analíticas
- 5 ambíguas/inválidas

A execução gera um log completo em `logs/benchmark_<timestamp>.json`.

## Tools implementadas

### Obrigatórias

1. `listar_colunas()`
2. `descrever_dados(colunas=None)`
3. `contar_valores(coluna, top_n=10)`
4. `filtrar(condicao)`
5. `agrupar_e_agregar(grupo, coluna, funcao, top_n=30, ordenar='desc')`
6. `correlacao(coluna_a, coluna_b, metodo='pearson')`
7. `detectar_outliers(coluna, metodo='iqr'|'zscore')`
8. `gerar_grafico(tipo, colunas, titulo='')`

### Extras

1. `top_municipios(coluna_ordenar, n=10, ordem='desc', estado=None)`

   Útil para perguntas como “quais municípios têm mais casos?” ou “qual município tem maior taxa por 100 mil?”. Evita retornar milhares de grupos ao LLM.

2. `resumir_por_estado(ordenar_por='confirmed', ordem='desc', top_n=27)`

   Útil para comparar UFs. Calcula corretamente as taxas agregadas por soma de casos e população, em vez de tirar média simples das taxas municipais.

## Estrutura

```text
projeto_agente_eda_covid_deepseek/
├── agent/
│   ├── agent.py          # loop ReAct
│   └── llm_client.py     # integração DeepSeek via OpenAI SDK
├── tools/
│   ├── base.py           # @tool, DataState e registry
│   ├── inspect_tools.py
│   ├── filter_tools.py
│   ├── stats_tools.py
│   ├── plot_tools.py
│   └── extra_tools.py
├── evaluation/
│   ├── benchmark.json
│   ├── benchmark.py
│   └── metrics.py
├── tests/
│   └── test_tools.py
├── scripts/
│   └── calcular_gabarito.py
├── data/
│   └── covid19.csv
├── outputs/
├── logs/
├── cli.py
├── config.py
├── requirements.txt
└── .env.example
```

## Como explicar na apresentação

A explicação mais importante é a separação de responsabilidades:

- DeepSeek decide qual tool usar.
- O `Agent` valida e executa a tool.
- A tool calcula em `pandas`.
- O resultado volta ao LLM para gerar texto.

Isso reduz alucinação porque a resposta é baseada no CSV, não em memória do modelo.
