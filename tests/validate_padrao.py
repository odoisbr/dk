#!/usr/bin/env python3
"""A estrutura canônica do projeto de design, e as regras que a cobram."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import padrao  # noqa: E402

errors = []

for pasta in ('0-apoio', '1-levantamento', '2-design', '3-entregaveis', 'registry'):
    if pasta not in padrao.PASTAS:
        errors.append(f'{pasta} deveria ser pasta canônica')

if len(padrao.ENTREGAVEIS) != 12:
    errors.append(f'esperados 12 entregáveis, há {len(padrao.ENTREGAVEIS)}')
for chave in ('briefing', 'visao', 'requisitos', 'ata', 'prototipo', 'handoff'):
    if chave not in padrao.ENTREGAVEIS:
        errors.append(f'entregável {chave} ausente')

if padrao.destino('ata') != '1-levantamento/atas':
    errors.append(f"destino da ata errado: {padrao.destino('ata')}")
if padrao.destino('requisitos') != '1-levantamento/requisitos':
    errors.append(f"destino de requisitos errado: {padrao.destino('requisitos')}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    achados = padrao.verificar(raiz)
    if 1 not in {a['regra'] for a in achados}:
        errors.append('projeto vazio deveria reprovar a regra 1')
    for a in achados:
        if not a.get('evidencia'):
            errors.append(f'achado sem evidência: {a}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    (raiz / '1-levantamento' / 'atas' / 'ata-2026-08-14.md').write_text(
        '## 1. Identificação\n', encoding='utf-8')
    achados = padrao.verificar(raiz)
    if 1 in {a['regra'] for a in achados}:
        errors.append('projeto com todas as pastas não deveria reprovar a regra 1')
    if 3 in {a['regra'] for a in achados}:
        errors.append('ata-2026-08-14.md está na convenção e não deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    (raiz / '1-levantamento' / 'atas' / 'Ata Reuniao FINAL v2.md').write_text(
        'x\n', encoding='utf-8')
    if 3 not in {a['regra'] for a in padrao.verificar(raiz)}:
        errors.append('nome fora da convenção deveria reprovar a regra 3')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    (raiz / '0-apoio' / 'reunioes').mkdir(parents=True, exist_ok=True)
    (raiz / '0-apoio' / 'reunioes' / 'transcricao.md').write_text(
        'x\n', encoding='utf-8')
    if 4 not in {a['regra'] for a in padrao.verificar(raiz)}:
        errors.append('insumo sem ata deveria reprovar a regra 4')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    (raiz / '1-levantamento' / 'requisitos' / 'requisitos.md').write_text(
        '# Requisitos\n\nsem o bloco.\n', encoding='utf-8')
    if 6 not in {a['regra'] for a in padrao.verificar(raiz)}:
        errors.append('documento sem bloco de validação deveria reprovar a regra 6')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
