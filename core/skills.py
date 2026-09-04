#!/usr/bin/env python3
"""Leitura do inventário de skills e das regras de portão.

Portão é a frase na `description` que amarra a skill a uma etapa. Skill com portão
não compete no catálogo genérico: ela só é considerada dentro da sua etapa. Apenas
as portas — uma por etapa, mais a porta geral — ficam sem portão."""
from __future__ import annotations
import re
from pathlib import Path
from typing import List

RAIZ = Path(__file__).resolve().parents[1]

ETAPAS = ('audit', 'levantar', 'entender', 'entregar', 'prototipar',
          'handoff', 'git')
PORTAS = {'dk'} | {f'dk-{e}' for e in ETAPAS}
# Oito portas: uma por etapa mais a porta geral. A 2.560 B (~640 tokens) o catálogo
# fixo custa 5% dos 49.678 B que o Kit anterior gastava em toda sessão, e cabe com
# folga no CORE CONTEXT de 3k tokens que a spec fixou.
#
# A folga não é convite: `MAX_PORTAS` trava em oito. Porta nova exige mudar este
# número, e mudar este número é uma decisão que aparece no diff.
ORCAMENTO_BYTES = 2560
MAX_PORTAS = 8

_PORTAO = re.compile(
    r'use quando a etapa\s+([a-zà-ú-]+)\s+do dk estiver ativa', re.I)


def frontmatter(path: Path) -> dict:
    texto = Path(path).read_text(encoding='utf-8')
    if not texto.startswith('---\n'):
        return {}
    bruto = texto.split('---', 2)[1]
    campos = {}
    for m in re.finditer(r'^([a-z][a-z-]*):\s*(.*?)(?=\n[a-z][a-z-]*:|\Z)',
                         bruto, re.S | re.M):
        campos[m.group(1)] = m.group(2).strip().strip('"\'')
    return campos


def inventario() -> List[dict]:
    itens = []
    for skill in sorted(RAIZ.glob('skills/*/SKILL.md')):
        campos = frontmatter(skill)
        descricao = campos.get('description', '')
        m = _PORTAO.search(descricao)
        etapa = m.group(1).lower() if m else ''
        itens.append({
            'nome': skill.parent.name,
            'description': descricao,
            'portao': bool(m),
            'etapa': etapa if etapa in ETAPAS else '',
        })
    return itens
