"""Cliente do LLM usando DeepSeek via SDK OpenAI.

A DeepSeek expõe uma API compatível com OpenAI. Mantemos esta camada isolada
para que o restante do projeto não dependa de detalhes do provedor.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any

from openai import OpenAI

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_THINKING,
    LLM_MODEL,
    MAX_TOKENS_PER_RESPONSE,
    REASONING_EFFORT,
)


@dataclass
class LLMResponse:
    text: str
    tool_calls: list[dict[str, Any]]
    raw_response: object
    raw_message: dict[str, Any]
    input_tokens: int
    output_tokens: int
    stop_reason: str
    latency_seconds: float


class LLMClient:
    """Cliente DeepSeek/OpenAI-compatible."""

    tool_format = "deepseek"

    def __init__(self, model: str = LLM_MODEL, api_key: str = DEEPSEEK_API_KEY):
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY não definida. Copie .env.example para .env e preencha a chave.")
        self.client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
        self.model = model

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], system: str = "") -> LLMResponse:
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": full_messages,
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": MAX_TOKENS_PER_RESPONSE,
            "stream": False,
        }

        # A API atual da DeepSeek aceita thinking via extra_body.
        # Caso o modelo/conta ignore, a chamada segue normal.
        if DEEPSEEK_THINKING in {"enabled", "disabled"}:
            kwargs["extra_body"] = {"thinking": {"type": DEEPSEEK_THINKING}}
            kwargs["reasoning_effort"] = REASONING_EFFORT

        inicio = time.perf_counter()
        resp = self.client.chat.completions.create(**kwargs)
        latencia = time.perf_counter() - inicio

        choice = resp.choices[0]
        message = choice.message
        texto = message.content or ""

        tool_calls = []
        raw_tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                args_text = tc.function.arguments or "{}"
                try:
                    args = json.loads(args_text)
                except json.JSONDecodeError:
                    args = {"_raw_arguments": args_text}
                tool_calls.append({"id": tc.id, "name": tc.function.name, "input": args})
                raw_tool_calls.append(
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {"name": tc.function.name, "arguments": args_text},
                    }
                )

        raw_message = {"role": "assistant", "content": texto or None}
        if raw_tool_calls:
            raw_message["tool_calls"] = raw_tool_calls

        usage = getattr(resp, "usage", None)
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)

        return LLMResponse(
            text=texto,
            tool_calls=tool_calls,
            raw_response=resp,
            raw_message=raw_message,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            stop_reason=choice.finish_reason or "unknown",
            latency_seconds=latencia,
        )
