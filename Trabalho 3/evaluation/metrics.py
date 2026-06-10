"""Métricas e comparadores do benchmark."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from config import NUMERIC_TOLERANCE


def extrair_numeros(texto: str) -> list[float]:
    """Extrai números em formatos pt-BR/en-US.

    Exemplos:
    - 5.589 -> 5589
    - 23.550.890 -> 23550890
    - 0,9175 -> 0.9175
    - 9.601,84 -> 9601.84
    """
    if not texto:
        return []

    texto = texto.replace("R$", "").replace("%", "")
    padrao = r"-?\d+(?:[\.,]\d+)*"
    valores = []

    for match in re.finditer(padrao, texto):
        s = match.group()

        if "," in s and "." in s:
            # Se vírgula vem depois do ponto: pt-BR, ex. 9.601,84
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            # Se ponto vem depois da vírgula: en-US, ex. 9,601.84
            else:
                s = s.replace(",", "")

        elif "," in s:
            partes = s.split(",")
            # 0,9175 deve ser decimal; 154,369 pode ser milhar em en-US
            if len(partes) == 2 and (len(partes[1]) != 3 or partes[0] == "0"):
                s = partes[0] + "." + partes[1]
            else:
                s = "".join(partes)

        elif "." in s:
            partes = s.split(".")
            # 0.9175 deve ser decimal; 154.369 deve ser milhar em pt-BR
            if len(partes) == 2 and (len(partes[1]) != 3 or partes[0] == "0"):
                s = s
            else:
                s = "".join(partes)

        try:
            valores.append(float(s))
        except ValueError:
            pass

    return valores

def comparar_numero(resposta: str, esperado: float) -> bool:
    nums = extrair_numeros(resposta)
    if not nums:
        return False
    tol = NUMERIC_TOLERANCE * max(1.0, abs(float(esperado)))
    return any(abs(n - float(esperado)) <= tol for n in nums)


def comparar_lista_strings(resposta: str, esperado: list[str]) -> bool:
    resposta_lower = resposta.lower()
    return all(str(item).lower() in resposta_lower for item in esperado)


def comparar_dict_numerico(resposta: str, esperado: dict[str, Any]) -> bool:
    """Verifica se cada chave aparece e se há número próximo no trecho da chave."""
    resposta_lower = resposta.lower()
    for chave, valor in esperado.items():
        chave_lower = str(chave).lower()
        if chave_lower not in resposta_lower:
            return False
        idx = resposta_lower.find(chave_lower)
        trecho = resposta[max(0, idx - 60) : idx + 160]
        nums = extrair_numeros(trecho)
        if not nums:
            return False
        tol = NUMERIC_TOLERANCE * max(1.0, abs(float(valor)))
        if not any(abs(n - float(valor)) <= tol for n in nums):
            return False
    return True


PALAVRAS_RECUSA = {
    "ambígua",
    "ambigua",
    "ambíguo",
    "ambiguo",
    "não está clara",
    "nao esta clara",
    "não entendi",
    "nao entendi",
    "esclarecer",
    "esclareça",
    "esclareca",
    "não consigo",
    "nao consigo",
    "não é possível",
    "nao e possivel",
    "inválida",
    "invalida",
    "coluna não existe",
    "coluna nao existe",
    "não existe",
    "nao existe",
    "não contém",
    "nao contem",
    "não possui",
    "nao possui",
    "não há",
    "nao ha",
    "fora do escopo",
    "preciso de critério",
    "preciso saber",
    "depende do critério",
}

def _normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[*_`#>|]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto

def comparar_categorica(resposta: str, esperado: str) -> bool:
    resposta_lower = _normalizar_texto(resposta)

    if esperado == "recusa":
        return any(p in resposta_lower for p in PALAVRAS_RECUSA)

    return esperado.lower() in resposta_lower

def avaliar_resposta(resposta: str, esperado, tipo_resposta: str) -> bool:
    if esperado is None:
        return False
    if tipo_resposta in {"numero_inteiro", "numero_float"}:
        return comparar_numero(resposta, float(esperado))
    if tipo_resposta == "lista_strings":
        return comparar_lista_strings(resposta, esperado)
    if tipo_resposta == "dict_numerico":
        return comparar_dict_numerico(resposta, esperado)
    if tipo_resposta == "categorica":
        return comparar_categorica(resposta, str(esperado))
    raise ValueError(f"Tipo de resposta desconhecido: {tipo_resposta}")


@dataclass
class BenchmarkSummary:
    total_perguntas: int
    acertos: int
    taxa_execucao_sucesso: float
    acuracia_geral: float
    acuracia_por_tipo: dict[str, float]
    tool_calls_media: float
    latencia_media: float
    input_tokens_total: int
    output_tokens_total: int

    def imprimir(self) -> None:
        print("\n" + "=" * 60)
        print("RESUMO DO BENCHMARK")
        print("=" * 60)
        print(f"Total de perguntas: {self.total_perguntas}")
        print(f"Acertos: {self.acertos}")
        print(f"Acurácia geral: {self.acuracia_geral:.1%}")
        print(f"Taxa de execução bem-sucedida: {self.taxa_execucao_sucesso:.1%}")
        print("\nAcurácia por tipo:")
        for tipo, acc in self.acuracia_por_tipo.items():
            print(f" - {tipo:12s}: {acc:.1%}")
        print(f"\nTool calls médias por pergunta: {self.tool_calls_media:.2f}")
        print(f"Latência média por pergunta: {self.latencia_media:.2f}s")
        print(f"Tokens entrada: {self.input_tokens_total}")
        print(f"Tokens saída: {self.output_tokens_total}")
        print("=" * 60)
