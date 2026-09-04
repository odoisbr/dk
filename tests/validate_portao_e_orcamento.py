#!/usr/bin/env python3
"""Só as portas ficam sem portão, e o catálogo fixo cabe no orçamento.

O Kit anterior carregava 49.678 B de description em toda sessão, ~12.420 tokens,
porque 191 das 275 skills não tinham portão de etapa (achados DK-004 e DK-502)."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import skills  # noqa: E402

errors = []
inventario = skills.inventario()

for item in inventario:
    nome = item['nome']
    if nome in skills.PORTAS:
        if item['portao']:
            errors.append(f'{nome}: é porta, não deveria ter portão')
    else:
        if not item['portao']:
            errors.append(
                f'{nome}: sem portão de etapa — toda skill que não é porta '
                'declara "Use quando a etapa <X> do DK estiver ativa"')
        if not item['etapa']:
            errors.append(f'{nome}: portão sem etapa reconhecível')

sem_portao = [i for i in inventario if not i['portao']]
custo = sum(len(i['description'].encode('utf-8')) for i in sem_portao)
if custo > skills.ORCAMENTO_BYTES:
    errors.append(
        f'catálogo fixo em {custo} B, orçamento é {skills.ORCAMENTO_BYTES} B '
        f'({len(sem_portao)} skills sem portão)')

print(f'catálogo fixo: {custo} B em {len(sem_portao)} skills sem portão '
      f'(orçamento {skills.ORCAMENTO_BYTES} B)')
for e in errors:
    print(e)
sys.exit(1 if errors else 0)
