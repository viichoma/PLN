# 5 perguntas extras para apresentação

Estas perguntas foram pensadas para complementar o benchmark atual sem remover nenhuma pergunta existente. Elas mostram: cálculo agregado, comparação entre estados, geração de gráfico e controle de alucinação/causalidade.

## p-001
**Pergunta:** Qual é a taxa de letalidade geral do dataset em percentual, calculada por óbitos totais divididos por casos confirmados totais?

**Resposta esperada:** 2,6130%

**Cálculo pandas:**
```python
round(float(df["deaths"].sum() / df["confirmed"].sum() * 100), 4)
```

**Por que é boa para apresentar:** mostra que o agente calcula uma métrica derivada, não apenas lê uma coluna pronta.

## p-002
**Pergunta:** Qual é a diferença de casos confirmados entre SP e RS?

**Resposta esperada:** 2.188.233

**Cálculo pandas:**
```python
g = df.groupby("state")["confirmed"].sum()
int(g.loc["SP"] - g.loc["RS"])
```

**Por que é boa para apresentar:** mostra comparação entre grupos após agregação por UF.

## p-003
**Pergunta:** Compare SP e RJ em óbitos totais: informe o total de cada um e a diferença entre eles.

**Resposta esperada:**
```json
{"SP": 154369, "RJ": 66422, "diferenca": 87947}
```

**Cálculo pandas:**
```python
g = df.groupby("state")["deaths"].sum()
{"SP": int(g.loc["SP"]), "RJ": int(g.loc["RJ"]), "diferenca": int(g.loc["SP"] - g.loc["RJ"])}
```

**Por que é boa para apresentar:** gera uma resposta composta, com dois totais e uma diferença.

## p-004
**Pergunta:** Gere um boxplot da coluna deaths e informe o caminho do arquivo PNG gerado.

**Resposta esperada:** a resposta deve conter `png` e apontar para um arquivo salvo em `outputs/`.

**Tool esperada:**
```python
gerar_grafico(tipo="boxplot", colunas=["deaths"])
```

**Por que é boa para apresentar:** mostra geração de visualização, além de resposta textual.

## p-005
**Pergunta:** É possível afirmar, apenas com este dataset, que maior população causa mais óbitos por COVID-19?

**Resposta esperada:** recusa / explicação de limitação causal.

**Justificativa:** o dataset permite análises descritivas e associações, mas não prova causalidade.

**Por que é boa para apresentar:** mostra controle de alucinação e maturidade crítica.

================================================================================
GABARITO DAS 5 PERGUNTAS EXTRAS PARA APRESENTAÇÃO
================================================================================
p-001 | Taxa de letalidade geral (%): 2.613
p-002 | Diferença de casos confirmados entre SP e RS: 2188233
p-003 | Óbitos SP/RJ/diferença: {'SP': 154369, 'RJ': 66422, 'diferenca': 87947}
p-004 | Esperado: caminho .png gerado por boxplot de deaths
p-005 | Esperado: recusa; associação descritiva não permite afirmar causalidade