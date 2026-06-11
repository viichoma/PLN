"""Tools extras específicas para o dataset COVID-19 Brasil.IO.

Estas tools ajudam a responder perguntas epidemiológicas comuns sem forçar o LLM
usar groupby genérico de maneira incorreta.
"""
from __future__ import annotations

import pandas as pd

from .base import state, tool


COLUNAS_TOP_VALIDAS = {
    "confirmed",
    "deaths",
    "estimated_population",
    "confirmed_per_100k_inhabitants",
    "death_rate",
}


@tool(
    description=(
        "Retorna ranking de municípios por uma métrica numérica do dataset COVID. "
        "Use para perguntas como: municípios com mais casos, mais óbitos, maior taxa por 100 mil, maior letalidade."
    ),
    parameters={
        "type": "object",
        "properties": {
            "coluna_ordenar": {
                "type": "string",
                "enum": sorted(COLUNAS_TOP_VALIDAS),
                "description": "Métrica usada para ordenar o ranking.",
            },
            "n": {"type": "integer", "description": "Quantidade de municípios. Default: 10."},
            "ordem": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "desc para maiores, asc para menores. Default: desc.",
            },
            "estado": {
                "type": "string",
                "description": "UF opcional para filtrar, ex.: SP, RJ, PR.",
            },
        },
        "required": ["coluna_ordenar"],
    },
)
def top_municipios(coluna_ordenar: str, n: int = 10, ordem: str = "desc", estado: str | None = None) -> dict:
    df = state.require_loaded()
    if coluna_ordenar not in df.columns:
        return {"erro": f"Coluna '{coluna_ordenar}' não existe."}
    if coluna_ordenar not in COLUNAS_TOP_VALIDAS:
        return {"erro": f"Coluna inválida para ranking. Use uma de {sorted(COLUNAS_TOP_VALIDAS)}."}
    if n <= 0:
        return {"erro": "n deve ser maior que zero."}
    if ordem not in {"asc", "desc"}:
        return {"erro": "ordem deve ser 'asc' ou 'desc'."}

    dados = df.copy()
    if estado:
        estado = estado.upper()
        dados = dados[dados["state"] == estado]
        if dados.empty:
            return {"erro": f"Nenhum município encontrado para o estado {estado}."}

    dados = dados.dropna(subset=[coluna_ordenar]).sort_values(coluna_ordenar, ascending=(ordem == "asc")).head(n)
    registros = []
    for _, row in dados.iterrows():
        registros.append(
            {
                "city": str(row["city"]),
                "state": str(row["state"]),
                "date": row["date"].date().isoformat() if hasattr(row["date"], "date") else str(row["date"]),
                "confirmed": int(row["confirmed"]),
                "deaths": int(row["deaths"]),
                "estimated_population": int(row["estimated_population"]) if pd.notna(row["estimated_population"]) else None,
                "confirmed_per_100k_inhabitants": round(float(row["confirmed_per_100k_inhabitants"]), 4)
                if pd.notna(row["confirmed_per_100k_inhabitants"])
                else None,
                "death_rate": round(float(row["death_rate"]), 4) if pd.notna(row["death_rate"]) else None,
                coluna_ordenar: round(float(row[coluna_ordenar]), 4) if pd.notna(row[coluna_ordenar]) else None,
            }
        )

    return {
        "coluna_ordenar": coluna_ordenar,
        "ordem": ordem,
        "estado": estado,
        "n": int(n),
        "registros": registros,
    }


@tool(
    description=(
        "Resume casos, óbitos, população, casos por 100 mil e taxa de letalidade por UF. "
        "Use para comparar estados. A taxa por 100 mil é calculada por soma de casos / soma de população, não média simples."
    ),
    parameters={
        "type": "object",
        "properties": {
            "ordenar_por": {
                "type": "string",
                "enum": ["confirmed", "deaths", "estimated_population", "confirmed_per_100k_inhabitants", "death_rate"],
                "description": "Métrica para ordenar. Default: confirmed.",
            },
            "ordem": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "desc para maiores, asc para menores. Default: desc.",
            },
            "top_n": {"type": "integer", "description": "Quantidade de UFs retornadas. Default: 27."},
        },
        "required": [],
    },
)
def resumir_por_estado(ordenar_por: str = "confirmed", ordem: str = "desc", top_n: int = 27) -> dict:
    df = state.require_loaded()
    if "state" not in df.columns:
        return {"erro": "Dataset não possui coluna 'state'."}
    if ordenar_por not in {"confirmed", "deaths", "estimated_population", "confirmed_per_100k_inhabitants", "death_rate"}:
        return {"erro": "ordenar_por inválido."}
    if ordem not in {"asc", "desc"}:
        return {"erro": "ordem deve ser 'asc' ou 'desc'."}
    if top_n <= 0:
        top_n = 27

    grouped = df.groupby("state", dropna=False).agg(
        municipalities=("city", "count"),
        confirmed=("confirmed", "sum"),
        deaths=("deaths", "sum"),
        estimated_population=("estimated_population", "sum"),
    )
    grouped["confirmed_per_100k_inhabitants"] = (
        grouped["confirmed"] / grouped["estimated_population"] * 100_000
    )
    grouped["death_rate"] = grouped["deaths"] / grouped["confirmed"]
    grouped = grouped.sort_values(ordenar_por, ascending=(ordem == "asc")).head(top_n)

    resultados = {}
    for uf, row in grouped.iterrows():
        resultados[str(uf)] = {
            "municipalities": int(row["municipalities"]),
            "confirmed": int(row["confirmed"]),
            "deaths": int(row["deaths"]),
            "estimated_population": int(row["estimated_population"]),
            "confirmed_per_100k_inhabitants": round(float(row["confirmed_per_100k_inhabitants"]), 4),
            "death_rate": round(float(row["death_rate"]), 4),
        }

    return {
        "ordenar_por": ordenar_por,
        "ordem": ordem,
        "top_n": int(top_n),
        "resultados": resultados,
    }
