#!/usr/bin/env python3
"""Alocação de id que respeita o contador do projeto.

O projeto real mantém `registry/id-counters.json` — `{"RN": 18, "RF": 86, ...}`.
Gerar id do zero a cada execução colide com o que já existe: a espinha produzia
`RN-001` e, num projeto com 18 regras, isso caía em cima da regra 1 dele.

Quem tem contador manda. Quem não tem, o DK deduz do maior id em uso — nunca
começa do 1 sem olhar."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, List

CONTADORES = 'registry/id-counters.json'
_ID = re.compile(r'^([A-Z]{2,4})-(\d+)$')


def _carregar(raiz: Path) -> Dict[str, int]:
    alvo = Path(raiz) / CONTADORES
    if not alvo.exists():
        return {}
    try:
        dados = json.loads(alvo.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}
    return {k: int(v) for k, v in dados.items() if str(v).isdigit()}


def maior_em_uso(itens: List[dict], prefixo: str) -> int:
    maior = 0
    for item in itens:
        m = _ID.match(str(item.get('id', '')))
        if m and m.group(1) == prefixo:
            maior = max(maior, int(m.group(2)))
    return maior


def base(raiz: Path, prefixo: str, itens: List[dict]) -> int:
    """De onde a numeração continua: o maior entre o contador e o que existe.

    Os dois, e não só o contador: contador desatualizado é comum, e confiar nele
    sozinho reescreve item existente."""
    return max(_carregar(raiz).get(prefixo, 0), maior_em_uso(itens, prefixo))


def novos(raiz: Path, prefixo: str, itens: List[dict], quantos: int) -> List[str]:
    inicio = base(raiz, prefixo, itens)
    return [f'{prefixo}-{inicio + i:03d}' for i in range(1, quantos + 1)]


def atualizar_contador(raiz: Path, avancos: Dict[str, int]) -> Dict[str, int]:
    """Devolve o mapa de contadores com os prefixos avançados. Não grava — quem
    grava é o envelope de escrita, dentro do escopo declarado.

    Recebe todos os avanços de uma vez, de propósito. A versão anterior aceitava
    um prefixo por chamada e relia o arquivo a cada uma: a segunda chamada
    devolvia um mapa fresco do disco e desfazia a primeira, e o contador de
    regras voltava a 18 depois de três regras terem sido criadas."""
    contadores = _carregar(raiz)
    for prefixo, ate in avancos.items():
        contadores[prefixo] = max(contadores.get(prefixo, 0), ate)
    return contadores
