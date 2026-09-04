#!/usr/bin/env python3
"""A cobertura cruza os registros entre si e com o entregável."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import cobertura, espinha, padrao, registry  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)

    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'não expira sozinho'},
        {'id': 'RN-002', 'enunciado': 'gestor revoga'},
        {'id': 'RN-003', 'enunciado': 'órfã sem requisito'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'convênio permanece ativo', 'deriva_de': 'RN-001'},
        {'id': 'REQ-002', 'titulo': 'revogação manual', 'deriva_de': 'RN-002'},
        {'id': 'REQ-003', 'titulo': 'sem âncora', 'deriva_de': 'RN-999'},
        {'id': 'REQ-004', 'titulo': 'sem campo de origem'},
    ])

    m = cobertura.matriz(raiz)

    if m['regras_sem_requisito'] != ['RN-003']:
        errors.append(f"regras sem requisito: {m['regras_sem_requisito']}")
    if set(m['requisitos_sem_regra']) != {'REQ-003', 'REQ-004'}:
        errors.append(f"requisitos sem regra: {m['requisitos_sem_regra']}")
    if m['totais']['regras'] != 3 or m['totais']['requisitos'] != 4:
        errors.append(f"totais errados: {m['totais']}")
    if len(m['requisitos_sem_entregavel']) != 4:
        errors.append('sem entregável, todos os requisitos estão descobertos')

    destino = raiz / padrao.destino('requisitos')
    destino.mkdir(parents=True, exist_ok=True)
    (destino / 'requisitos-2026-09-04.html').write_text(
        '<p>REQ-001 e REQ-002 estão cobertos.</p>', encoding='utf-8')

    m2 = cobertura.matriz(raiz)
    if set(m2['requisitos_sem_entregavel']) != {'REQ-003', 'REQ-004'}:
        errors.append(f"após o entregável: {m2['requisitos_sem_entregavel']}")

antigo = espinha.cobertura(
    [{'id': 'REQ-001', 'deriva_de': 'RN-001'}],
    [{'id': 'RN-001'}, {'id': 'RN-002'}])
if antigo['regras_sem_requisito'] != ['RN-002']:
    errors.append('espinha.cobertura mudou de comportamento ao delegar')
if antigo['total_regras'] != 2 or antigo['total_requisitos'] != 1:
    errors.append(f'totais da espinha mudaram: {antigo}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
