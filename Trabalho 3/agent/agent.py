"""Agente principal: loop ReAct (pensar -> agir -> observar)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from typing import Any

from config import LLM_PROVIDER, MAX_AGENT_ITERATIONS
from tools import all_tools_for_llm, get_tool_by_name, state

from .llm_client import LLMClient, LLMResponse


@dataclass
class Step:
    tipo: str  # llm_text | tool_call | tool_result | erro
    conteudo: dict[str, Any] | str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResult:
    pergunta: str
    resposta_final: str
    sucesso: bool
    trajetoria: list[Step]
    total_iteracoes: int
    total_tool_calls: int
    input_tokens: int
    output_tokens: int
    latencia_total: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "pergunta": self.pergunta,
            "resposta_final": self.resposta_final,
            "sucesso": self.sucesso,
            "total_iteracoes": self.total_iteracoes,
            "total_tool_calls": self.total_tool_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latencia_total": round(self.latencia_total, 4),
            "trajetoria": [s.__dict__ for s in self.trajetoria],
        }


SYSTEM_PROMPT = """
Você é um agente de análise exploratória de dados (EDA) em português.

Contexto do dataset carregado: COVID-19 Brasil.IO por município.
Colunas esperadas: date, state, city, place_type, confirmed, deaths, is_last,
estimated_population, city_ibge_code, confirmed_per_100k_inhabitants, death_rate.

Regras obrigatórias:
1. Responda com fatos calculados pelas tools. Não invente valores.
2. Se não souber as colunas, chame listar_colunas antes de operar.
3. Use nomes exatos de colunas.
4. Para rankings de municípios, prefira top_municipios.
5. Para comparação entre estados, prefira resumir_por_estado, pois ela calcula taxas por soma agregada.
6. Para perguntas ambíguas, peça esclarecimento ou diga que não é possível responder.
7. Não faça previsão/modelagem preditiva; se pedirem previsão, explique que está fora do escopo.
8. Use o menor número de tool calls necessário.
9. Formate números em português e explique rapidamente qual cálculo foi feito.
10. Quando responder números do benchmark, inclua o valor exato retornado pela tool, sem arredondar inteiros.
11. Para datas, sempre inclua também o formato ISO AAAA-MM-DD.
12. Se o usuário pedir gráfico, chame obrigatoriamente gerar_grafico.
13. Para perguntas ambíguas, responda explicitamente com a frase: "Pergunta ambígua: preciso de esclarecimento".
14. Não exclua categorias especiais, como "Importados/Indefinidos", a menos que a pergunta peça explicitamente.
""".strip()


class Agent:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()
        provider = getattr(self.llm, "tool_format", LLM_PROVIDER)
        self.tools_para_llm = all_tools_for_llm(provider)

    def _executar_tool(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        nome = tool_call.get("name")
        argumentos = tool_call.get("input", {}) or {}
        if "_raw_arguments" in argumentos:
            return {"erro": f"Argumentos da tool vieram em JSON inválido: {argumentos['_raw_arguments']}"}

        spec = get_tool_by_name(nome)
        if spec is None:
            return {"erro": f"Tool '{nome}' não encontrada."}

        try:
            return spec.function(**argumentos)
        except TypeError as e:
            return {"erro": f"Argumentos inválidos para '{nome}': {e}"}
        except Exception as e:  # salvaguarda: o agente não deve quebrar
            return {"erro": f"Erro ao executar '{nome}': {type(e).__name__}: {e}"}

    def perguntar(self, pergunta: str) -> AgentResult:
        try:
            state.require_loaded()
        except RuntimeError as e:
            return AgentResult(pergunta, str(e), False, [], 0, 0, 0, 0, 0.0)

        messages: list[dict[str, Any]] = [{"role": "user", "content": pergunta}]
        trajetoria: list[Step] = []
        total_input = 0
        total_output = 0
        latencia_total = 0.0
        total_tool_calls = 0

        for iteracao in range(MAX_AGENT_ITERATIONS):
            resposta: LLMResponse = self.llm.chat(messages=messages, tools=self.tools_para_llm, system=SYSTEM_PROMPT)
            total_input += resposta.input_tokens
            total_output += resposta.output_tokens
            latencia_total += resposta.latency_seconds

            if resposta.text:
                trajetoria.append(Step("llm_text", resposta.text))

            if not resposta.tool_calls:
                return AgentResult(
                    pergunta=pergunta,
                    resposta_final=resposta.text or "(sem resposta)",
                    sucesso=True,
                    trajetoria=trajetoria,
                    total_iteracoes=iteracao + 1,
                    total_tool_calls=total_tool_calls,
                    input_tokens=total_input,
                    output_tokens=total_output,
                    latencia_total=latencia_total,
                )

            messages.append(resposta.raw_message)

            for tc in resposta.tool_calls:
                total_tool_calls += 1
                trajetoria.append(Step("tool_call", {"nome": tc["name"], "argumentos": tc["input"]}))
                resultado = self._executar_tool(tc)
                trajetoria.append(Step("tool_result", resultado))
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(resultado, ensure_ascii=False, default=str),
                    }
                )

        return AgentResult(
            pergunta=pergunta,
            resposta_final=f"Limite de {MAX_AGENT_ITERATIONS} iterações atingido sem resposta final.",
            sucesso=False,
            trajetoria=trajetoria,
            total_iteracoes=MAX_AGENT_ITERATIONS,
            total_tool_calls=total_tool_calls,
            input_tokens=total_input,
            output_tokens=total_output,
            latencia_total=latencia_total,
        )
