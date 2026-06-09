"""Infraestrutura comum das ferramentas do agente.

Define:
- DataState: mantém o DataFrame carregado em memória;
- @tool: decorador de registro;
- formatos de tools para OpenAI/DeepSeek e Anthropic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd

from config import CSV_SEPARATOR


class DataState:
    """Estado compartilhado entre as tools.

    O DataFrame é carregado uma vez pela CLI ou pelo benchmark. As tools acessam
    esse mesmo estado, sem recarregar o CSV a cada chamada.
    """

    def __init__(self) -> None:
        self.df: pd.DataFrame | None = None
        self.path: str | None = None

    def load(self, path: str) -> None:
        """Carrega um CSV e faz pequenas normalizações úteis para EDA."""
        df = pd.read_csv(path, sep=CSV_SEPARATOR)

        # Normalização leve para o dataset COVID-19 Brasil.IO.
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Garante que booleanos lidos como texto sejam convertidos quando aplicável.
        for col in df.columns:
            if df[col].dtype == "object":
                valores = set(str(v).lower() for v in df[col].dropna().unique()[:5])
                if valores and valores.issubset({"true", "false"}):
                    df[col] = df[col].map(lambda x: str(x).lower() == "true")

        self.df = df
        self.path = path

    def require_loaded(self) -> pd.DataFrame:
        if self.df is None:
            raise RuntimeError("Nenhum dataset carregado. Carregue um CSV antes de chamar as tools.")
        return self.df


state = DataState()


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    function: Callable[..., dict]


TOOL_REGISTRY: list[ToolSpec] = []


def tool(description: str, parameters: dict[str, Any]):
    """Registra uma função Python como tool disponível ao LLM."""

    def decorator(func: Callable[..., dict]):
        TOOL_REGISTRY.append(
            ToolSpec(
                name=func.__name__,
                description=description,
                parameters=parameters,
                function=func,
            )
        )
        return func

    return decorator


def get_tool_by_name(name: str) -> ToolSpec | None:
    for spec in TOOL_REGISTRY:
        if spec.name == name:
            return spec
    return None


def all_tools_for_llm(provider: str = "deepseek") -> list[dict[str, Any]]:
    """Retorna as tools no formato esperado pelo provedor.

    DeepSeek usa API compatível com OpenAI:
    {"type": "function", "function": {name, description, parameters}}
    """
    if provider.lower() in {"deepseek", "openai"}:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in TOOL_REGISTRY
        ]

    if provider.lower() == "anthropic":
        return [
            {"name": t.name, "description": t.description, "input_schema": t.parameters}
            for t in TOOL_REGISTRY
        ]

    raise ValueError(f"Provider não suportado: {provider}")
