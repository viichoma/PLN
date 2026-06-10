# Explicação do projeto

## 1. Ideia central

O projeto é um agente de análise exploratória de dados. Ele recebe uma pergunta em português sobre um CSV e responde usando ferramentas Python.

A diferença para um chatbot comum é esta: o modelo não deve responder “de cabeça”. Ele precisa chamar uma tool, e a tool calcula em `pandas`.

Exemplo:

```text
Pergunta: Qual estado tem mais óbitos?
1. O LLM decide chamar resumir_por_estado(ordenar_por='deaths').
2. O Agent executa a função Python.
3. A função faz groupby em pandas.
4. O resultado volta ao LLM.
5. O LLM escreve: SP tem o maior total de óbitos...
```

## 2. Por que DeepSeek

A DeepSeek foi usada porque possui API compatível com OpenAI. Isso simplifica o código: usamos o pacote `openai`, mas configuramos `base_url=https://api.deepseek.com`.

Arquivo principal: `agent/llm_client.py`.

Esse arquivo:

- cria `OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)`;
- envia mensagens e tools para `client.chat.completions.create()`;
- lê `message.tool_calls` quando o modelo pede ferramentas;
- devolve uma estrutura padronizada `LLMResponse` para o `Agent`.

## 3. Loop do agente

Arquivo principal: `agent/agent.py`.

O método `Agent.perguntar()` faz:

1. inicia o histórico com a pergunta do usuário;
2. chama o DeepSeek passando o prompt do sistema e a lista de tools;
3. se o modelo responder sem tool, encerra;
4. se o modelo pedir tool, executa a função Python;
5. coloca o resultado da tool no histórico;
6. chama o modelo novamente;
7. repete até obter resposta final ou atingir limite de iterações.

O limite `MAX_AGENT_ITERATIONS` evita loop infinito.

## 4. Tools obrigatórias

### `listar_colunas()`

Mostra nomes, tipos, nulos e exemplo de valor. Deve ser chamada quando o agente ainda não sabe a estrutura do CSV.

### `descrever_dados()`

Resume estatísticas de colunas numéricas, categóricas e datas.

### `contar_valores(coluna)`

Faz `value_counts()`. Serve para saber distribuição de UFs, cidades, flags etc.

### `filtrar(condicao)`

Usa `df.query(condicao)`. Exemplo: `state == 'SP'`. Retorna quantidade de linhas e estatísticas numéricas do recorte.

### `agrupar_e_agregar(grupo, coluna, funcao)`

Faz `df.groupby(grupo)[coluna].agg(funcao)`. Serve para somas, médias, contagens por grupo.

### `correlacao(coluna_a, coluna_b)`

Calcula correlação Pearson ou Spearman entre duas colunas numéricas.

### `detectar_outliers(coluna)`

Detecta outliers por IQR ou z-score. O z-score foi implementado para completar o TODO do projeto base.

### `gerar_grafico(tipo, colunas)`

Gera PNG em `outputs/`. O LLM não recebe imagem; ele recebe o caminho do arquivo.

## 5. Tools extras adicionadas

### `top_municipios()`

Motivo: o dataset tem mais de 5 mil municípios. Um `groupby` por cidade pode gerar retorno enorme. Essa tool retorna apenas um ranking limitado.

Exemplos de perguntas que ela viabiliza:

- “Quais são os 10 municípios com mais casos?”
- “Qual município tem maior taxa por 100 mil habitantes?”
- “No RJ, quais municípios têm mais óbitos?”

### `resumir_por_estado()`

Motivo: comparar UFs exige agregação correta. Para taxa por 100 mil, não se deve fazer média simples das taxas municipais. O correto é:

```text
casos totais da UF / população total da UF * 100.000
```

Essa tool calcula isso diretamente.

Exemplos:

- “Qual estado tem mais casos?”
- “Qual estado tem maior letalidade?”
- “Qual estado tem maior taxa de casos por 100 mil habitantes?”

## 6. Benchmark

Arquivo: `evaluation/benchmark.json`.

Possui 30 perguntas:

- 10 factuais simples;
- 15 analíticas;
- 5 ambíguas ou inválidas.

Os gabaritos foram calculados com `scripts/calcular_gabarito.py`.

O executor `evaluation/benchmark.py` chama o agente para cada pergunta, compara com o gabarito e salva log completo.

## 7. Pontos para defender na banca

1. O LLM não executa código diretamente; ele só solicita tools.
2. As tools são determinísticas e testáveis com `pytest`.
3. O projeto registra trajetória, tokens, latência e tool calls.
4. Perguntas ambíguas são tratadas como recusa ou pedido de esclarecimento.
5. A tool extra `resumir_por_estado` evita erro estatístico comum: média de taxas municipais em vez de taxa agregada.

## 8. Limitações

- O benchmark automático usa comparadores heurísticos; pode errar se a resposta correta vier com outra redação.
- A API tem custo por token; por isso as tools retornam dados resumidos.
- O dataset é um retrato acumulado por município, não uma base clínica individual.
- O agente não faz previsão nem modelagem causal.
