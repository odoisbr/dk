#!/usr/bin/env python3
"""Registros do projeto: requisitos, regras, atas, decisões, pendências.

`upsert` é o coração: item com id que já existe é fundido, não anexado. O Kit
anterior gravava e não relia, e por isso o mesmo requisito voltava duplicado a
cada levantamento (achado DK-104)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Tuple

from core import io


def _caminho(raiz: Path, nome: str) -> Path:
    return Path(raiz) / 'registry' / f'{nome}.json'


def carregar(raiz: Path, nome: str) -> List[dict]:
    path = _caminho(raiz, nome)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding='utf-8'))


def gravar(raiz: Path, nome: str, itens: List[dict]) -> None:
    io.atomic_json(_caminho(raiz, nome), itens)


def upsert(itens: List[dict], novo: dict, chave: str = 'id') -> Tuple[List[dict], str]:
    """Funde `novo` na lista. Campo ausente em `novo` preserva o valor anterior."""
    saida = [dict(i) for i in itens]
    for i, existente in enumerate(saida):
        if existente.get(chave) == novo.get(chave):
            fundido = dict(existente)
            fundido.update(novo)
            saida[i] = fundido
            return saida, 'atualizado'
    saida.append(dict(novo))
    return saida, 'criado'
