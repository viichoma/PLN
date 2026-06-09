"""Tools de inspeção do dataset."""
from __future__ import annotations

import pandas as pd

from .base import state, tool


def _json_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value.item() if hasattr(value, "item") else value


@tool(
    description=(
        "Lista colunas, tipos, quantidade de linhas e quantidade de nulos. "
        "Use antes de escolher nomes de colunas."
    ),
    parameters={"type": "object", "properties": {}, "required": []},
)
def listar_colunas() -> dict:
    df = state.require_loaded()
    return {
        "total_linhas": int(len(df)),
        "total_colunas": int(len(df.columns)),
        "colunas": [
            {
                "nome": col,
                "tipo": str(df[col].dtype),
                "nulos": int(df[col].isna().sum()),
                "exemplo": _json_value(df[col].dropna().iloc[0]) if df[col].dropna().shape[0] else None,
            }
            for col in df.columns
        ],
    }


@tool(
    description=(
        "Descreve estatísticas do dataset ou de colunas específicas. "
        "Inclui numéricas, categóricas, booleanas e datas."
    ),
    parameters={
        "type": "object",
        "properties": {
            "colunas": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de colunas. Se omitida ou vazia, descreve todas.",
            }
        },
        "required": [],
    },
)
def descrever_dados(colunas: list[str] | None = None) -> dict:
    df = state.require_loaded()
    if colunas:
        invalidas = [c for c in colunas if c not in df.columns]
        if invalidas:
            return {"erro": f"Colunas inexistentes: {invalidas}"}
        df = df[colunas]

    resultado: dict = {"linhas": int(len(df)), "colunas": int(len(df.columns))}

    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        resultado["numericas"] = {
            col: {k: round(float(v), 4) for k, v in stats.items() if pd.notna(v)}
            for col, stats in num_df.describe().to_dict().items()
        }

    cat_bool_df = df.select_dtypes(include=["object", "category", "bool"])
    if not cat_bool_df.empty:
        resultado["categoricas"] = {}
        for col in cat_bool_df.columns:
            vc = cat_bool_df[col].value_counts(dropna=False)
            resultado["categoricas"][col] = {
                "valores_unicos": int(df[col].nunique(dropna=True)),
                "mais_frequente": str(vc.index[0]) if len(vc) else None,
                "frequencia_top": int(vc.iloc[0]) if len(vc) else 0,
                "nulos": int(df[col].isna().sum()),
            }

    date_df = df.select_dtypes(include=["datetime", "datetimetz"])
    if not date_df.empty:
        resultado["datas"] = {
            col: {
                "min": date_df[col].min().date().isoformat() if pd.notna(date_df[col].min()) else None,
                "max": date_df[col].max().date().isoformat() if pd.notna(date_df[col].max()) else None,
                "valores_unicos": int(date_df[col].nunique(dropna=True)),
            }
            for col in date_df.columns
        }

    return resultado


@tool(
    description=(
        "Conta os valores mais frequentes de uma coluna. "
        "Boa para estados, municípios, tipos e flags booleanas."
    ),
    parameters={
        "type": "object",
        "properties": {
            "coluna": {"type": "string", "description": "Nome da coluna."},
            "top_n": {
                "type": "integer",
                "description": "Quantidade de valores mais frequentes. Default: 10.",
            },
        },
        "required": ["coluna"],
    },
)
def contar_valores(coluna: str, top_n: int = 10) -> dict:
    df = state.require_loaded()
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não existe no dataset."}
    if top_n <= 0:
        return {"erro": "top_n deve ser maior que zero."}

    contagem = df[coluna].value_counts(dropna=False).head(top_n)
    return {
        "coluna": coluna,
        "total_valores_unicos": int(df[coluna].nunique(dropna=True)),
        "valores_nulos": int(df[coluna].isna().sum()),
        "distribuicao": {str(k): int(v) for k, v in contagem.items()},
    }
