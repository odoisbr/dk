#!/usr/bin/env python3
"""Toda skill com portão é nomeada pelo agente da sua etapa.

Portão sem enumeração apaga capacidade: a skill deixa o catálogo e ninguém
consegue chegar nela."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import skills  # noqa: E402

errors = []
inventario = skills.inventario()
por_etapa = {}
for item in inventario:
    if item['etapa']:
        por_etapa.setdefault(item['etapa'], []).append(item['nome'])

for etapa, nomes in sorted(por_etapa.items()):
    agente = RAIZ / 'agents' / f'dk-{etapa}.md'
    if not agente.exists():
        errors.append(f'etapa {etapa}: falta agents/dk-{etapa}.md')
        continue
    texto = agente.read_text(encoding='utf-8')
    if '## Skills desta etapa' not in texto:
        errors.append(f'agents/dk-{etapa}.md: falta a seção "## Skills desta etapa"')
    for nome in nomes:
        if nome not in texto:
            errors.append(f'agents/dk-{etapa}.md não enumera {nome}')

for porta in sorted(skills.PORTAS):
    if porta == 'dk':
        continue
    etapa = porta[len('dk-'):]
    if (RAIZ / 'skills' / porta / 'SKILL.md').exists():
        if not (RAIZ / 'agents' / f'dk-{etapa}.md').exists():
            errors.append(f'porta {porta} existe sem agents/dk-{etapa}.md')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
