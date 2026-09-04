#!/usr/bin/env python3
"""Tokens DTCG: folha malformada e referência que não resolve."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, tokens  # noqa: E402

errors = []

BOM = {
    'cor': {
        'primaria': {'$value': '#009CC5', '$type': 'color'},
        'texto': {'$value': '{cor.primaria}', '$type': 'color'},
    },
    'espaco': {'2': {'$value': '8px', '$type': 'dimension'}},
}


def montar(raiz: Path, arvore):
    io.atomic_write(raiz / tokens.ARQUIVO,
                    json.dumps(arvore, ensure_ascii=False, indent=2))


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, BOM)
    achados = tokens.verificar(raiz)
    if achados:
        errors.append(f'árvore válida não deveria ter achado: {achados}')

    nomes = {c for c, _ in tokens.folhas(BOM)}
    if nomes != {'cor.primaria', 'cor.texto', 'espaco.2'}:
        errors.append(f'caminho de folha errado: {nomes}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, {'cor': {'x': {'$value': '#fff'}}})
    if 'TOK-SEM-TIPO' not in {a['id'] for a in tokens.verificar(raiz)}:
        errors.append('folha sem $type deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, {'cor': {'x': {'$value': '#fff', '$type': 'cor'}}})
    if 'TOK-TIPO' not in {a['id'] for a in tokens.verificar(raiz)}:
        errors.append('$type fora do conjunto deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, {'cor': {'texto': {'$value': '{cor.fantasma}', '$type': 'color'}}})
    ach = [a for a in tokens.verificar(raiz) if a['id'] == 'TOK-REFERENCIA']
    if not ach:
        errors.append('referência não resolvida deveria reprovar')
    elif ach[0]['impacto'] != 'alto':
        errors.append('referência quebrada não quebra o build; por isso é alto')
    elif 'cor.fantasma' not in ach[0]['evidencia']:
        errors.append('a evidência não nomeia a referência quebrada')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    io.atomic_write(raiz / tokens.ARQUIVO, '{ nao e json')
    if 'TOK-JSON' not in {a['id'] for a in tokens.verificar(raiz)}:
        errors.append('tokens.json inválido deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    if tokens.verificar(Path(d)):
        errors.append('projeto sem tokens.json não deveria ter achado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
