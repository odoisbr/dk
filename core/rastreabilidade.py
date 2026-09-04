#!/usr/bin/env python3
"""Matriz bidirecional: de onde o requisito veio e para onde ele foi.

Uma linha por requisito. Para trás, a regra e a citação que o originaram; para
frente, o entregável onde aparece e o changeset que o tocou. Requisito sem origem
é marcado, nunca preenchido por dedução."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from core import padrao, registry


def _changesets(raiz: Path) -> List[dict]:
    pasta = Path(raiz) / '.dk' / 'changesets'
    if not pasta.is_dir():
        return []
    saida = []
    for arq in sorted(pasta.glob('*.json')):
        try:
            saida.append(json.loads(arq.read_text(encoding='utf-8')))
        except json.JSONDecodeError:
            continue
    return saida


def _entregaveis(raiz: Path) -> List[tuple]:
    saida = []
    for chave in ('requisitos', 'visao', 'ata'):
        pasta = Path(raiz) / padrao.destino(chave)
        if not pasta.is_dir():
            continue
        for arq in sorted(pasta.iterdir()):
            if arq.suffix.lower() in ('.html', '.md'):
                saida.append((str(arq.relative_to(raiz)),
                              arq.read_text(encoding='utf-8', errors='replace')))
    return saida


def matriz(raiz: Path) -> List[Dict]:
    raiz = Path(raiz)
    regras = {r['id']: r for r in registry.carregar(raiz, 'regras')}
    docs = _entregaveis(raiz)
    changesets = _changesets(raiz)

    linhas = []
    for q in registry.carregar(raiz, 'requisitos'):
        origem = q.get('deriva_de')
        regra = regras.get(origem) if origem else None
        onde = [caminho for caminho, texto in docs if q['id'] in texto]
        tocado = [cs['id'] for cs in changesets
                  if q['id'] in (cs.get('requisitos') or [])]

        if regra:
            estado = 'rastreado' if onde else 'sem entregável'
        else:
            estado = 'sem origem'

        linhas.append({
            'requisito': q['id'],
            'titulo': q.get('titulo', ''),
            'regra': regra['id'] if regra else '',
            'citacao': (regra or {}).get('citacao', ''),
            'fonte': (regra or {}).get('fonte', ''),
            'entregaveis': onde,
            'changesets': tocado,
            'estado': estado,
        })
    return linhas


def markdown(linhas: List[Dict]) -> str:
    saida = ['| Requisito | Origem | Citação | Entregável | Changeset | Estado |',
             '|---|---|---|---|---|---|']
    for l in linhas:
        saida.append(
            f"| {l['requisito']} | {l['regra'] or '—'} | "
            f"{(l['citacao'] or '—')[:50]} | "
            f"{', '.join(l['entregaveis']) or '—'} | "
            f"{', '.join(l['changesets']) or '—'} | {l['estado']} |")
    return '\n'.join(saida)
