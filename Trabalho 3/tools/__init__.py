"""Pacote de tools.

Importar os módulos abaixo executa os decoradores @tool e registra tudo em TOOL_REGISTRY.
"""
from .base import TOOL_REGISTRY, ToolSpec, all_tools_for_llm, get_tool_by_name, state, tool

from . import inspect_tools  # noqa: F401
from . import filter_tools  # noqa: F401
from . import stats_tools  # noqa: F401
from . import plot_tools  # noqa: F401
from . import extra_tools  # noqa: F401

__all__ = [
    "state",
    "tool",
    "TOOL_REGISTRY",
    "ToolSpec",
    "get_tool_by_name",
    "all_tools_for_llm",
]
