#!/usr/bin/env python3
"""A matriz liga o requisito à sua origem e ao seu destino, nos dois sentidos."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, padrao, rastreabilidade, registry  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'o gestor revoga',
         'citacao': 'quem tira do ar é o gestor', 'fonte': 'ata 14/08'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'revogação manual', 'deriva_de': 'RN-001'},
        {'id': 'REQ-002', 'titulo': 'sem origem'},
    ])
    io.atomic_write(raiz / padrao.destino('requisitos') / 'requisitos.html',
                    '<p>REQ-001 consta aqui</p>')
    io.atomic_write(raiz / '.dk' / 'changesets' / 'CS-001.json',
                    json.dumps({'id': 'CS-001', 'title': 'ajuste',
                                'affected': ['2-design/prototipo'],
                                'requisitos': ['REQ-001']}))

    linhas = rastreabilidade.matriz(raiz)
    por_id = {l['requisito']: l for l in linhas}

    if len(linhas) != 2:
        errors.append(f'esperadas 2 linhas, vieram {len(linhas)}')

    a = por_id.get('REQ-001', {})
    if a.get('regra') != 'RN-001':
        errors.append(f"REQ-001 sem a regra de origem: {a.get('regra')}")
    if 'quem tira do ar' not in (a.get('citacao') or ''):
        errors.append('a citação de origem não chegou à matriz')
    if not a.get('entregaveis'):
        errors.append('REQ-001 aparece no entregável e a matriz não viu')
    if 'CS-001' not in (a.get('changesets') or []):
        errors.append('o changeset que tocou o requisito não foi ligado')
    if a.get('estado') != 'rastreado':
        errors.append(f"REQ-001 deveria estar rastreado: {a.get('estado')}")

    b = por_id.get('REQ-002', {})
    if b.get('regra'):
        errors.append('REQ-002 não tem origem; a matriz não pode inventar uma')
    if b.get('estado') != 'sem origem':
        errors.append(f"REQ-002 deveria ser marcado: {b.get('estado')}")

    md = rastreabilidade.markdown(linhas)
    if 'REQ-001' not in md or '| ' not in md:
        errors.append('markdown() não produziu tabela com os requisitos')
    if md.count('\n') != len(linhas) + 1:
        errors.append('a tabela não tem uma linha por requisito')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
