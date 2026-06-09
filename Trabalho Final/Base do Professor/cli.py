"""
Interface de linha de comando (CLI) do agente.

Execute com:
    python cli.py

Comandos especiais durante a sessão:
    /sair         - encerra
    /trajetoria   - mostra a trajetória da última pergunta
    /custo        - mostra custo/tokens acumulados na sessão
    /ajuda        - lista de comandos
"""

"""Interface de linha de comando do agente.

Execute:
    python cli.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent import Agent
from config import DATASET_PATH
from tools import state

console = Console()


def imprimir_boas_vindas() -> None:
    console.print(
        Panel.fit(
            "[bold blue]Agente EDA COVID-19[/bold blue]\n"
            "Pergunte em português sobre o CSV carregado. Digite /ajuda para comandos.",
            border_style="blue",
        )
    )


def imprimir_ajuda() -> None:
    tabela = Table(title="Comandos disponíveis")
    tabela.add_column("Comando", style="cyan")
    tabela.add_column("Descrição")
    tabela.add_row("/sair", "Encerra a sessão")
    tabela.add_row("/ajuda", "Mostra esta ajuda")
    tabela.add_row("/trajetoria", "Mostra tools chamadas na última pergunta")
    tabela.add_row("/custo", "Mostra tokens, latência e tool calls acumulados")
    tabela.add_row("/colunas", "Mostra colunas carregadas sem chamar LLM")
    console.print(tabela)


def imprimir_colunas() -> None:
    df = state.require_loaded()
    tabela = Table(title="Colunas do dataset")
    tabela.add_column("Coluna", style="cyan")
    tabela.add_column("Tipo")
    tabela.add_column("Nulos", justify="right")
    for col in df.columns:
        tabela.add_row(col, str(df[col].dtype), str(int(df[col].isna().sum())))
    console.print(tabela)


def imprimir_trajetoria(resultado) -> None:
    if resultado is None:
        console.print("[yellow]Sem trajetória. Faça uma pergunta primeiro.[/yellow]")
        return
    tabela = Table(title=f"Trajetória: {resultado.pergunta[:70]}")
    tabela.add_column("#", style="dim", width=4)
    tabela.add_column("Tipo", style="cyan")
    tabela.add_column("Conteúdo")
    for i, passo in enumerate(resultado.trajetoria, start=1):
        conteudo = str(passo.conteudo)
        if len(conteudo) > 220:
            conteudo = conteudo[:220] + "..."
        tabela.add_row(str(i), passo.tipo, conteudo)
    console.print(tabela)


def main() -> None:
    if not Path(DATASET_PATH).exists():
        console.print(
            f"[red]Erro:[/red] dataset não encontrado em {DATASET_PATH}.\n"
            "Coloque covid19.csv na pasta data/ ou ajuste DATASET_PATH no .env."
        )
        sys.exit(1)

    state.load(str(DATASET_PATH))
    console.print(
        f"[green]✓[/green] Dataset carregado: [bold]{DATASET_PATH.name}[/bold] "
        f"({len(state.df)} linhas × {len(state.df.columns)} colunas)"
    )

    try:
        agente = Agent()
    except RuntimeError as e:
        console.print(f"[red]Erro ao inicializar LLM:[/red] {e}")
        sys.exit(1)

    imprimir_boas_vindas()
    ultima_resposta = None
    custo = {"input": 0, "output": 0, "latencia": 0.0, "tool_calls": 0}

    while True:
        try:
            pergunta = console.input("\n[bold cyan]> [/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Encerrado.[/dim]")
            break

        if not pergunta:
            continue
        if pergunta == "/sair":
            console.print("[dim]Encerrado.[/dim]")
            break
        if pergunta == "/ajuda":
            imprimir_ajuda()
            continue
        if pergunta == "/colunas":
            imprimir_colunas()
            continue
        if pergunta == "/trajetoria":
            imprimir_trajetoria(ultima_resposta)
            continue
        if pergunta == "/custo":
            console.print(
                f"Tokens entrada: {custo['input']}\n"
                f"Tokens saída: {custo['output']}\n"
                f"Tool calls: {custo['tool_calls']}\n"
                f"Latência total: {custo['latencia']:.2f}s"
            )
            continue

        with console.status("[dim]Consultando DeepSeek e executando tools...[/dim]"):
            resultado = agente.perguntar(pergunta)

        ultima_resposta = resultado
        custo["input"] += resultado.input_tokens
        custo["output"] += resultado.output_tokens
        custo["latencia"] += resultado.latencia_total
        custo["tool_calls"] += resultado.total_tool_calls

        console.print(
            Panel(
                resultado.resposta_final,
                border_style="green" if resultado.sucesso else "red",
                title=(
                    f"[dim]{resultado.total_tool_calls} tool calls · "
                    f"{resultado.latencia_total:.2f}s · "
                    f"{resultado.input_tokens + resultado.output_tokens} tokens[/dim]"
                ),
            )
        )


if __name__ == "__main__":
    main()
