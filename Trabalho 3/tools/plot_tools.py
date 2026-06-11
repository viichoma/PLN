"""Tool de visualização: gera gráficos em PNG."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import OUTPUTS_DIR
from .base import state, tool


TIPOS_VALIDOS = {"hist", "histograma", "boxplot", "scatter", "barplot", "linha"}


def _gerar_nome_arquivo(tipo: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return OUTPUTS_DIR / f"plot_{tipo}_{ts}.png"


@tool(
    description=(
        "Gera gráfico e salva em PNG. Tipos: hist/histograma (1 numérica), boxplot (1 numérica "
        "ou categoria+numérica), scatter (2 numéricas), barplot (1 categórica), linha (x,y)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "tipo": {"type": "string", "enum": sorted(TIPOS_VALIDOS)},
            "colunas": {"type": "array", "items": {"type": "string"}},
            "titulo": {"type": "string", "description": "Título opcional."},
        },
        "required": ["tipo", "colunas"],
    },
)
def gerar_grafico(tipo: str, colunas: list[str], titulo: str = "") -> dict:
    df = state.require_loaded()
    if tipo not in TIPOS_VALIDOS:
        return {"erro": f"Tipo '{tipo}' inválido. Use um de {sorted(TIPOS_VALIDOS)}."}
    for col in colunas:
        if col not in df.columns:
            return {"erro": f"Coluna '{col}' não existe."}

    fig, ax = plt.subplots(figsize=(10, 6))
    try:
        if tipo in {"hist", "histograma"}:
            if len(colunas) != 1:
                return {"erro": "Histograma requer exatamente 1 coluna."}
            if not pd.api.types.is_numeric_dtype(df[colunas[0]]):
                return {"erro": "Histograma requer coluna numérica."}
            df[colunas[0]].dropna().plot(kind="hist", bins=30, ax=ax, edgecolor="black")
            ax.set_xlabel(colunas[0])
            ax.set_ylabel("Frequência")

        elif tipo == "boxplot":
            if len(colunas) == 1:
                if not pd.api.types.is_numeric_dtype(df[colunas[0]]):
                    return {"erro": "Boxplot com 1 coluna requer coluna numérica."}
                df.boxplot(column=colunas[0], ax=ax)
            elif len(colunas) == 2:
                df.boxplot(column=colunas[1], by=colunas[0], ax=ax)
                fig.suptitle("")
            else:
                return {"erro": "Boxplot aceita 1 coluna ou 2 colunas (categoria, numérica)."}

        elif tipo == "scatter":
            if len(colunas) != 2:
                return {"erro": "Scatter requer exatamente 2 colunas."}
            if not all(pd.api.types.is_numeric_dtype(df[c]) for c in colunas):
                return {"erro": "Scatter requer duas colunas numéricas."}
            df.plot.scatter(x=colunas[0], y=colunas[1], ax=ax, alpha=0.5)

        elif tipo == "barplot":
            if len(colunas) != 1:
                return {"erro": "Barplot requer exatamente 1 coluna."}
            df[colunas[0]].value_counts().head(20).plot(kind="bar", ax=ax)
            ax.set_xlabel(colunas[0])
            ax.set_ylabel("Contagem")

        elif tipo == "linha":
            if len(colunas) != 2:
                return {"erro": "Linha requer 2 colunas: eixo x e eixo y."}
            dados = df.sort_values(colunas[0])
            dados.plot(x=colunas[0], y=colunas[1], ax=ax, kind="line")

        ax.set_title(titulo or f"{tipo}: {', '.join(colunas)}")
        fig.tight_layout()
        caminho = _gerar_nome_arquivo(tipo)
        fig.savefig(caminho, dpi=130)
        return {
            "tipo": tipo,
            "colunas": colunas,
            "arquivo_gerado": str(caminho),
            "mensagem": f"Gráfico salvo em {caminho.name}",
        }
    except Exception as e:
        return {"erro": f"Erro ao gerar gráfico: {type(e).__name__}: {e}"}
    finally:
        plt.close(fig)
