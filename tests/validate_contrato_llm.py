#!/usr/bin/env python3
"""Os dois contratos existem, têm papéis diferentes, e nada os copia.

llms.txt é roteador: curto, aponta. llms-full.txt é contrato: completo, tem os
invariantes. O CLAUDE.md referencia os dois e não repete nenhum."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []

curto = RAIZ / 'llms.txt'
longo = RAIZ / 'llms-full.txt'
claude = RAIZ / 'CLAUDE.md'

for f in (curto, longo, claude):
    if not f.exists():
        errors.append(f'{f.name} não existe')

if not errors:
    t_curto = curto.read_text(encoding='utf-8')
    t_longo = longo.read_text(encoding='utf-8')
    t_claude = claude.read_text(encoding='utf-8')

    if len(t_curto.encode('utf-8')) > 4096:
        errors.append(f'llms.txt tem {len(t_curto.encode("utf-8"))} B — '
                      'é roteador, não enciclopédia; limite 4096 B')
    if 'NON-NEGOTIABLE INVARIANTS' not in t_longo:
        errors.append('llms-full.txt sem a seção NON-NEGOTIABLE INVARIANTS')
    if len(t_longo) <= len(t_curto):
        errors.append('llms-full.txt não é mais completo que o llms.txt')

    if 'llms-full.txt' not in t_claude:
        errors.append('CLAUDE.md não referencia o llms-full.txt')
    if len(t_claude.encode('utf-8')) > 2048:
        errors.append(f'CLAUDE.md tem {len(t_claude.encode("utf-8"))} B — '
                      'ele referencia, não repete; limite 2048 B')

    for bloco in [b for b in t_longo.split('\n\n') if len(b) > 200]:
        if bloco in t_claude:
            errors.append('CLAUDE.md copia um bloco do llms-full.txt')
            break

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
