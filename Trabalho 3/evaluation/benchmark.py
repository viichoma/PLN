"""Executor do benchmark.

Execute:
    python -m evaluation.benchmark
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from agent import Agent
from config import BENCHMARK_FILE, DATASET_PATH, LOGS_DIR
from tools import state

from .metrics import BenchmarkSummary, avaliar_resposta

console = Console()


def carregar_benchmark(caminho: Path = BENCHMARK_FILE) -> list[dict]:
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados.get("perguntas", [])


def rodar_benchmark() -> None:
    if not Path(DATASET_PATH).exists():
        console.print(f"[red]Dataset não encontrado: {DATASET_PATH}[/red]")
        return

    state.load(str(DATASET_PATH))
    console.print(f"[green]✓[/green] Dataset: {DATASET_PATH.name} ({len(state.df)} linhas × {len(state.df.columns)} colunas)")

    perguntas = carregar_benchmark()
    if not perguntas:
        console.print("[red]Benchmark vazio.[/red]")
        return
    console.print(f"[green]✓[/green] Benchmark carregado: {len(perguntas)} perguntas")

    try:
        agente = Agent()
    except RuntimeError as e:
        console.print(f"[red]Erro ao criar Agent:[/red] {e}")
        return

    resultados = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Avaliando", total=len(perguntas))
        for p in perguntas:
            progress.update(task, description=f"[{p['id']}] {p['pergunta'][:60]}...")
            resultado = agente.perguntar(p["pergunta"])
            correto = False
            if resultado.sucesso:
                try:
                    correto = avaliar_resposta(resultado.resposta_final, p.get("resposta_esperada"), p["tipo_resposta"])
                except Exception as e:
                    console.print(f"[yellow]Erro ao avaliar {p['id']}: {e}[/yellow]")

            resultados.append(
                {
                    "id": p["id"],
                    "tipo": p["tipo"],
                    "pergunta": p["pergunta"],
                    "resposta_esperada": p.get("resposta_esperada"),
                    "resposta_obtida": resultado.resposta_final,
                    "correto": correto,
                    "execucao_sucesso": resultado.sucesso,
                    "tool_calls": resultado.total_tool_calls,
                    "iteracoes": resultado.total_iteracoes,
                    "input_tokens": resultado.input_tokens,
                    "output_tokens": resultado.output_tokens,
                    "latencia_seg": round(resultado.latencia_total, 4),
                    "trajetoria": [{"tipo": s.tipo, "conteudo": s.conteudo} for s in resultado.trajetoria],
                }
            )
            progress.advance(task)

    total = len(resultados)
    acertos = sum(r["correto"] for r in resultados)
    exec_ok = sum(r["execucao_sucesso"] for r in resultados)

    por_tipo_total = defaultdict(int)
    por_tipo_correto = defaultdict(int)
    for r in resultados:
        por_tipo_total[r["tipo"]] += 1
        if r["correto"]:
            por_tipo_correto[r["tipo"]] += 1

    resumo = BenchmarkSummary(
        total_perguntas=total,
        acertos=acertos,
        taxa_execucao_sucesso=exec_ok / total if total else 0,
        acuracia_geral=acertos / total if total else 0,
        acuracia_por_tipo={t: por_tipo_correto[t] / por_tipo_total[t] for t in por_tipo_total},
        tool_calls_media=sum(r["tool_calls"] for r in resultados) / total if total else 0,
        latencia_media=sum(r["latencia_seg"] for r in resultados) / total if total else 0,
        input_tokens_total=sum(r["input_tokens"] for r in resultados),
        output_tokens_total=sum(r["output_tokens"] for r in resultados),
    )
    resumo.imprimir()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"benchmark_{ts}.json"
    log_data = {
        "timestamp": ts,
        "dataset": str(DATASET_PATH),
        "resumo": resumo.__dict__,
        "resultados": resultados,
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)
    console.print(f"\n[green]✓[/green] Log salvo em [bold]{log_path}[/bold]")


if __name__ == "__main__":
    rodar_benchmark()
