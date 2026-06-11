"""Script auxiliar para recalcular respostas do benchmark em pandas.

Versão com as perguntas atuais + 5 perguntas extras para apresentação.

Onde colocar no projeto:
    Trabalho 3/scripts/calcular_gabarito_mais_5.py

Como executar a partir da pasta Trabalho 3/:
    python scripts/calcular_gabarito_mais_5.py

Pré-requisito:
    O arquivo data/covid19.csv precisa existir no projeto.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "covid19.csv"


def carregar_dataset() -> pd.DataFrame:
    """Carrega o CSV usado no trabalho."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado em {DATASET_PATH}. "
            "Execute o script dentro da estrutura do projeto, com data/covid19.csv presente."
        )
    return pd.read_csv(DATASET_PATH, parse_dates=["date"])


def resumo_por_estado(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa o dataset por UF e calcula totais e taxas agregadas."""
    g = df.groupby("state").agg(
        municipalities=("city", "count"),
        confirmed=("confirmed", "sum"),
        deaths=("deaths", "sum"),
        estimated_population=("estimated_population", "sum"),
    )
    g["confirmed_per_100k_inhabitants"] = (
        g["confirmed"] / g["estimated_population"] * 100_000
    )
    g["death_rate"] = g["deaths"] / g["confirmed"]
    return g


def contar_outliers_iqr(serie: pd.Series) -> int:
    """Conta outliers usando o critério IQR."""
    s = serie.dropna()
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    return int(((s < limite_inferior) | (s > limite_superior)).sum())


def contar_outliers_zscore(serie: pd.Series, limite: float = 3.0) -> int:
    """Conta outliers usando z-score absoluto maior que o limite."""
    s = serie.dropna()
    z = (s - s.mean()) / s.std(ddof=0)
    return int((np.abs(z) > limite).sum())

def spearman_sem_scipy(coluna_a: pd.Series, coluna_b: pd.Series) -> float:
    pares = pd.concat([coluna_a, coluna_b], axis=1).dropna()
    rank_a = pares.iloc[:, 0].rank(method="average")
    rank_b = pares.iloc[:, 1].rank(method="average")
    return float(rank_a.corr(rank_b, method="pearson"))

def main() -> None:
    df = carregar_dataset()
    g = resumo_por_estado(df)

    print("=" * 80)
    print("GABARITO DAS PERGUNTAS ATUAIS")
    print("=" * 80)

    print("f-001 | Linhas:", len(df))
    print("f-002 | Colunas:", list(df.columns))
    print("f-003 | UFs distintas:", df["state"].nunique())
    print("f-004 | Municípios distintos:", df["city"].nunique())
    print("f-005 | Data máxima:", df["date"].max().date())
    print("f-006 | Data mínima:", df["date"].min().date())
    print("f-007 | Total confirmed:", int(df["confirmed"].sum()))
    print("f-008 | Total deaths:", int(df["deaths"].sum()))
    print("f-009 | Nulos estimated_population:", int(df["estimated_population"].isna().sum()))
    print("f-010 | Município com mais casos:", df.loc[df["confirmed"].idxmax(), "city"])

    print("a-001 | Top 3 estados por casos:", g.sort_values("confirmed", ascending=False)["confirmed"].head(3).to_dict())
    print("a-002 | Top 3 estados por óbitos:", g.sort_values("deaths", ascending=False)["deaths"].head(3).to_dict())
    print("a-003 | SP casos por 100 mil habitantes:", round(float(g.loc["SP", "confirmed_per_100k_inhabitants"]), 4))
    print("a-004 | UF maior casos por 100 mil habitantes:", g["confirmed_per_100k_inhabitants"].idxmax())
    print("a-005 | UF maior letalidade agregada:", g["death_rate"].idxmax())
    print("a-006 | Linhas/municípios de SP:", int((df["state"] == "SP").sum()))
    print("a-007 | Confirmed PR:", int(g.loc["PR", "confirmed"]))
    print("a-008 | RJ município com mais óbitos:", df[df["state"] == "RJ"].sort_values("deaths", ascending=False).iloc[0]["city"])
    print("a-009 | Top 3 municípios por óbitos:")
    print(df.sort_values("deaths", ascending=False)[["city", "state", "deaths"]].head(3).to_string(index=False))
    print("a-010 | Corr Pearson confirmed/deaths:", round(float(df["confirmed"].corr(df["deaths"], method="pearson")), 4))
    print("a-011 | Corr Spearman confirmed/deaths:", round(spearman_sem_scipy(df["confirmed"], df["deaths"]), 4))
    print("a-012 | Outliers IQR confirmed:", contar_outliers_iqr(df["confirmed"]))
    print("a-013 | Outliers z-score deaths:", contar_outliers_zscore(df["deaths"]))
    print("a-014 | Município maior confirmed_per_100k:", df.dropna(subset=["confirmed_per_100k_inhabitants"]).sort_values("confirmed_per_100k_inhabitants", ascending=False).iloc[0]["city"])
    print("a-015 | Confirmed Ourinhos:", int(df[df["city"] == "Ourinhos"].iloc[0]["confirmed"]))

    print("m-001 | Esperado: recusa / pedido de critério")
    print("m-002 | Esperado: recusa; não há coluna de vacinação")
    print("m-003 | Esperado: recusa; não há coluna de internações")
    print("m-004 | Esperado: recusa; pergunta subjetiva/causal")
    print("m-005 | Esperado: recusa; previsão/modelagem está fora do escopo")

    print("g-001 | Esperado: caminho .png gerado por histograma de confirmed")
    print("g-002 | Esperado: caminho .png gerado por scatter confirmed x deaths")
    print("g-003 | Esperado: caminho .png gerado por barplot de state")

    print()
    print("=" * 80)
    print("GABARITO DAS 5 PERGUNTAS EXTRAS PARA APRESENTAÇÃO")
    print("=" * 80)

    total_confirmed = int(df["confirmed"].sum())
    total_deaths = int(df["deaths"].sum())
    taxa_letalidade_geral_percentual = total_deaths / total_confirmed * 100
    diferenca_confirmed_sp_rs = int(g.loc["SP", "confirmed"] - g.loc["RS", "confirmed"])
    deaths_sp = int(g.loc["SP", "deaths"])
    deaths_rj = int(g.loc["RJ", "deaths"])
    diferenca_deaths_sp_rj = deaths_sp - deaths_rj

    print("p-001 | Taxa de letalidade geral (%):", round(float(taxa_letalidade_geral_percentual), 4))
    print("p-002 | Diferença de casos confirmados entre SP e RS:", diferenca_confirmed_sp_rs)
    print("p-003 | Óbitos SP/RJ/diferença:", {"SP": deaths_sp, "RJ": deaths_rj, "diferenca": diferenca_deaths_sp_rj})
    print("p-004 | Esperado: caminho .png gerado por boxplot de deaths")
    print("p-005 | Esperado: recusa; associação descritiva não permite afirmar causalidade")


if __name__ == "__main__":
    main()
