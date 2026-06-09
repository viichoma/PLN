"""Tools estatísticas: correlação e outliers."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import state, tool


@tool(
    description="Calcula correlação Pearson ou Spearman entre duas colunas numéricas.",
    parameters={
        "type": "object",
        "properties": {
            "coluna_a": {"type": "string"},
            "coluna_b": {"type": "string"},
            "metodo": {
                "type": "string",
                "enum": ["pearson", "spearman"],
                "description": "Método de correlação. Default: pearson.",
            },
        },
        "required": ["coluna_a", "coluna_b"],
    },
)
def correlacao(coluna_a: str, coluna_b: str, metodo: str = "pearson") -> dict:
    df = state.require_loaded()
    for col in (coluna_a, coluna_b):
        if col not in df.columns:
            return {"erro": f"Coluna '{col}' não existe."}
        if not pd.api.types.is_numeric_dtype(df[col]):
            return {"erro": f"Coluna '{col}' não é numérica (tipo: {df[col].dtype})."}
    if metodo not in {"pearson", "spearman"}:
        return {"erro": "Método inválido. Use 'pearson' ou 'spearman'."}

    pares = df[[coluna_a, coluna_b]].dropna()
    if len(pares) < 2:
        return {"erro": "Não há pares válidos suficientes para calcular correlação."}

    valor = pares[coluna_a].corr(pares[coluna_b], method=metodo)
    if pd.isna(valor):
        return {"erro": "Correlação indefinida; uma das colunas pode ser constante."}

    abs_val = abs(float(valor))
    if abs_val < 0.1:
        intensidade = "desprezível"
    elif abs_val < 0.3:
        intensidade = "fraca"
    elif abs_val < 0.7:
        intensidade = "moderada"
    else:
        intensidade = "forte"
    sinal = "positiva" if valor > 0 else "negativa"

    return {
        "coluna_a": coluna_a,
        "coluna_b": coluna_b,
        "metodo": metodo,
        "pares_validos": int(len(pares)),
        "correlacao": round(float(valor), 4),
        "interpretacao": f"{intensidade} e {sinal}",
    }


@tool(
    description="Detecta outliers em coluna numérica por IQR ou z-score.",
    parameters={
        "type": "object",
        "properties": {
            "coluna": {"type": "string"},
            "metodo": {
                "type": "string",
                "enum": ["iqr", "zscore"],
                "description": "Método. Default: iqr.",
            },
        },
        "required": ["coluna"],
    },
)
def detectar_outliers(coluna: str, metodo: str = "iqr") -> dict:
    df = state.require_loaded()
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não existe."}
    if not pd.api.types.is_numeric_dtype(df[coluna]):
        return {"erro": f"Coluna '{coluna}' não é numérica."}

    serie = df[coluna].dropna()
    if serie.empty:
        return {"erro": f"Coluna '{coluna}' não possui valores válidos."}

    if metodo == "iqr":
        q1 = serie.quantile(0.25)
        q3 = serie.quantile(0.75)
        iqr = q3 - q1
        limite_inf = q1 - 1.5 * iqr
        limite_sup = q3 + 1.5 * iqr
        outliers = serie[(serie < limite_inf) | (serie > limite_sup)]
        return {
            "coluna": coluna,
            "metodo": "iqr",
            "limite_inferior": round(float(limite_inf), 4),
            "limite_superior": round(float(limite_sup), 4),
            "total_outliers": int(len(outliers)),
            "porcentagem": round(len(outliers) / len(serie) * 100, 2),
            "exemplos": [round(float(v), 4) for v in outliers.sort_values(ascending=False).head(5)],
        }

    if metodo == "zscore":
        media = serie.mean()
        desvio = serie.std(ddof=0)
        if desvio == 0 or pd.isna(desvio):
            return {"erro": "Desvio-padrão zero; z-score não pode ser calculado."}
        z = (serie - media) / desvio
        outliers = serie[np.abs(z) > 3]
        exemplos = outliers.sort_values(ascending=False).head(5)
        return {
            "coluna": coluna,
            "metodo": "zscore",
            "media": round(float(media), 4),
            "desvio_padrao": round(float(desvio), 4),
            "limite_z": 3,
            "total_outliers": int(len(outliers)),
            "porcentagem": round(len(outliers) / len(serie) * 100, 2),
            "exemplos": [round(float(v), 4) for v in exemplos],
        }

    return {"erro": f"Método '{metodo}' não reconhecido. Use 'iqr' ou 'zscore'."}
