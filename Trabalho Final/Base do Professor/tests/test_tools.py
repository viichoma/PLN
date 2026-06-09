from __future__ import annotations

import pandas as pd
import pytest

from tools import state
from tools.inspect_tools import listar_colunas, descrever_dados, contar_valores
from tools.filter_tools import filtrar, agrupar_e_agregar
from tools.stats_tools import correlacao, detectar_outliers
from tools.extra_tools import resumir_por_estado, top_municipios


@pytest.fixture(autouse=True)
def carregar_dataset_sintetico():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2022-01-01"] * 8),
            "state": ["SP", "SP", "RJ", "RJ", "MG", "MG", "SP", "RJ"],
            "city": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "place_type": ["city"] * 8,
            "confirmed": [100, 200, 500, 600, 50, 70, 10000, 40],
            "deaths": [5, 10, 40, 60, 1, 2, 500, 0],
            "is_last": [True] * 8,
            "estimated_population": [1000, 2000, 5000, 6000, 1000, 1000, 20000, 800],
            "city_ibge_code": [1, 2, 3, 4, 5, 6, 7, 8],
            "confirmed_per_100k_inhabitants": [10000, 10000, 10000, 10000, 5000, 7000, 50000, 5000],
            "death_rate": [0.05, 0.05, 0.08, 0.10, 0.02, 0.0286, 0.05, 0.0],
        }
    )
    state.df = df
    state.path = "teste"
    yield
    state.df = None
    state.path = None


def test_listar_colunas_basico():
    r = listar_colunas()
    nomes = [c["nome"] for c in r["colunas"]]
    assert "confirmed" in nomes
    assert r["total_linhas"] == 8


def test_descrever_dados_tem_numericas_e_categoricas():
    r = descrever_dados()
    assert "numericas" in r
    assert "categoricas" in r
    assert "confirmed" in r["numericas"]
    assert "state" in r["categoricas"]


def test_contar_valores_estado():
    r = contar_valores("state")
    assert r["distribuicao"]["SP"] == 3
    assert r["distribuicao"]["RJ"] == 3


def test_filtrar_estado_sp():
    r = filtrar("state == 'SP'")
    assert r["linhas_resultantes"] == 3
    assert r["estatisticas"]["confirmed"]["soma"] == pytest.approx(10300)


def test_agrupar_e_agregar_soma_confirmed_por_estado():
    r = agrupar_e_agregar("state", "confirmed", "sum", top_n=3)
    assert r["resultados"]["SP"] == pytest.approx(10300)
    assert r["resultados"]["RJ"] == pytest.approx(1140)


def test_correlacao_confirmed_deaths():
    r = correlacao("confirmed", "deaths")
    assert "correlacao" in r
    assert r["correlacao"] > 0.9


def test_detectar_outliers_iqr():
    r = detectar_outliers("confirmed", metodo="iqr")
    assert r["total_outliers"] >= 1
    assert 10000.0 in r["exemplos"]


def test_detectar_outliers_zscore_implementado():
    r = detectar_outliers("confirmed", metodo="zscore")
    assert "erro" not in r
    assert r["metodo"] == "zscore"


def test_top_municipios_por_casos():
    r = top_municipios("confirmed", n=1)
    assert r["registros"][0]["city"] == "G"
    assert r["registros"][0]["confirmed"] == 10000


def test_resumir_por_estado_calcula_taxa_agregada():
    r = resumir_por_estado(ordenar_por="confirmed", top_n=1)
    assert "SP" in r["resultados"]
    sp = r["resultados"]["SP"]
    assert sp["confirmed"] == 10300
    assert sp["estimated_population"] == 23000
    assert sp["confirmed_per_100k_inhabitants"] == pytest.approx(44782.6087, abs=0.001)


def test_coluna_inexistente_retorna_erro():
    assert "erro" in contar_valores("nao_existe")
    assert "erro" in correlacao("confirmed", "nao_existe")
    assert "erro" in top_municipios("nao_existe")
