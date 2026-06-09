"""Tools de filtragem e agregação."""
from __future__ import annotations

import pandas as pd

from .base import state, tool


FUNCOES_VALIDAS = {"mean", "median", "sum", "min", "max", "count", "std"}


@tool(
    description=(
        "Filtra o dataset usando sintaxe pandas query e retorna resumo do subconjunto. "
        "Exemplos: state == 'SP'; confirmed > 10000; city == 'Ourinhos'."
    ),
    parameters={
        "type": "object",
        "properties": {
            "condicao": {"type": "string", "description": "Expressão pandas query()."}
        },
        "required": ["condicao"],
    },
)
def filtrar(condicao: str) -> dict:
    df = state.require_loaded()
    try:
        filtrado = df.query(condicao)
    except Exception as e:
        return {
            "erro": f"Expressão inválida: {e}",
            "dica": "Use nomes exatos das colunas e coloque textos entre aspas. Ex.: state == 'SP'",
        }

    if filtrado.empty:
        return {
            "condicao": condicao,
            "linhas_resultantes": 0,
            "porcentagem_do_total": 0.0,
            "aviso": "Nenhuma linha satisfaz a condição.",
        }

    estatisticas = {}
    for col in filtrado.select_dtypes(include="number").columns:
        serie = filtrado[col].dropna()
        if serie.empty:
            continue
        estatisticas[col] = {
            "media": round(float(serie.mean()), 4),
            "mediana": round(float(serie.median()), 4),
            "min": round(float(serie.min()), 4),
            "max": round(float(serie.max()), 4),
            "soma": round(float(serie.sum()), 4),
        }

    return {
        "condicao": condicao,
        "linhas_resultantes": int(len(filtrado)),
        "porcentagem_do_total": round(len(filtrado) / len(df) * 100, 2),
        "estatisticas": estatisticas,
    }


@tool(
    description=(
        "Agrupa por uma coluna e agrega outra coluna com mean, median, sum, min, max, count ou std. "
        "Pode ordenar e limitar top_n para não gerar respostas enormes."
    ),
    parameters={
        "type": "object",
        "properties": {
            "grupo": {"type": "string", "description": "Coluna de agrupamento."},
            "coluna": {"type": "string", "description": "Coluna a agregar."},
            "funcao": {
                "type": "string",
                "enum": sorted(FUNCOES_VALIDAS),
                "description": "Função de agregação.",
            },
            "top_n": {
                "type": "integer",
                "description": "Quantidade máxima de grupos retornados. Default: 30.",
            },
            "ordenar": {
                "type": "string",
                "enum": ["asc", "desc", "none"],
                "description": "Ordenação dos resultados. Default: desc.",
            },
        },
        "required": ["grupo", "coluna", "funcao"],
    },
)
def agrupar_e_agregar(
    grupo: str,
    coluna: str,
    funcao: str,
    top_n: int = 30,
    ordenar: str = "desc",
) -> dict:
    df = state.require_loaded()
    if grupo not in df.columns:
        return {"erro": f"Coluna de grupo '{grupo}' não existe."}
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não existe."}
    if funcao not in FUNCOES_VALIDAS:
        return {"erro": f"Função '{funcao}' inválida. Use uma de {sorted(FUNCOES_VALIDAS)}."}
    if funcao != "count" and not pd.api.types.is_numeric_dtype(df[coluna]):
        return {"erro": f"Função '{funcao}' requer coluna numérica; '{coluna}' é {df[coluna].dtype}."}
    if top_n <= 0:
        top_n = 30

    serie = df.groupby(grupo, dropna=False)[coluna].agg(funcao)
    if ordenar == "desc":
        serie = serie.sort_values(ascending=False)
    elif ordenar == "asc":
        serie = serie.sort_values(ascending=True)

    total_grupos = int(len(serie))
    serie = serie.head(top_n)
    return {
        "grupo": grupo,
        "coluna": coluna,
        "funcao": funcao,
        "total_grupos": total_grupos,
        "top_n_retornado": int(len(serie)),
        "resultados": {
            str(k): round(float(v), 4) if pd.notna(v) else None for k, v in serie.items()
        },
    }
