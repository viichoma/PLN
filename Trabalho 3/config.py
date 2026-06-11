"""Configurações centralizadas do projeto.

Tudo que varia entre execuções fica aqui: caminhos, modelo, limites e chaves.
O projeto foi adaptado para DeepSeek usando a API compatível com OpenAI.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CAMINHOS
# ============================================================
ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOGS_DIR = ROOT_DIR / "logs"
EVAL_DIR = ROOT_DIR / "evaluation"

for directory in (DATA_DIR, OUTPUTS_DIR, LOGS_DIR):
    directory.mkdir(exist_ok=True)

# ============================================================
# DATASET
# ============================================================
DATASET_PATH = Path(os.getenv("DATASET_PATH", str(DATA_DIR / "covid19.csv")))
CSV_SEPARATOR = os.getenv("CSV_SEPARATOR", ",")

# ============================================================
# LLM / DEEPSEEK
# ============================================================
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
# Em 2026 a documentação da DeepSeek recomenda deepseek-v4-flash/pro.
# deepseek-chat ainda pode funcionar, mas está marcado para depreciação.
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v4-flash")

# Desative thinking para reduzir custo/latência e melhorar tool-calling no modo simples.
DEEPSEEK_THINKING = os.getenv("DEEPSEEK_THINKING", "disabled")
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "high")

# ============================================================
# AGENTE
# ============================================================
MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "8"))
MAX_TOKENS_PER_RESPONSE = int(os.getenv("MAX_TOKENS_PER_RESPONSE", "900"))

# ============================================================
# AVALIAÇÃO
# ============================================================
BENCHMARK_FILE = EVAL_DIR / "benchmark.json"
NUMERIC_TOLERANCE = float(os.getenv("NUMERIC_TOLERANCE", "0.05"))
