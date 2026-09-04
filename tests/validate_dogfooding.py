#!/usr/bin/env python3
"""O dk consegue mapear a si mesmo, e se reconhece como projeto DK.

É o teste que a spec chama de dogfooding: se o auditor não entende o próprio
repositório, ele não entende repositório nenhum."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []

r = subprocess.run(
    [sys.executable, str(RAIZ / 'bin' / 'dk'), 'audit',
     '--projeto', str(RAIZ), '--json'],
    capture_output=True, text=True)

if r.returncode != 0:
    errors.append(f'audit sobre o próprio dk falhou: {r.stdout}{r.stderr}')
else:
    m = json.loads(r.stdout)

    if m['projeto']['tipo'] != 'plugin':
        errors.append(f"o dk deveria se detectar como plugin, "
                      f"veio {m['projeto']['tipo']}")
    if 'python' not in m['projeto']['stack']:
        errors.append(f"stack sem python: {m['projeto']['stack']}")
    for ev in m['projeto']['evidencias']:
        alvo = ev.split(':')[0]
        if not (RAIZ / alvo).exists():
            errors.append(f'evidência aponta para arquivo inexistente: {ev}')

    if not m['conformidade']['usa_dk']:
        errors.append('o dk não se reconhece como projeto DK')
    for a in m['conformidade']['achados']:
        if a['impacto'] == 'alto':
            errors.append(f"achado alto no próprio dk: {a['titulo']} — "
                          f"{a['evidencia']}")

    nomes = {i['caminho'] for i in m['importantes']}
    for esperado in ('llms.txt', 'CLAUDE.md', '.claude-plugin/plugin.json'):
        if esperado not in nomes:
            errors.append(f'{esperado} deveria ser importante no próprio dk')

    if m['metricas']['arquivos'] < 20:
        errors.append(f"mapeou só {m['metricas']['arquivos']} arquivos do dk")

    for caminho in nomes:
        if not (RAIZ / caminho).exists():
            errors.append(f'o mapa aponta {caminho}, que não existe')

    if '.git' not in json.dumps(m['ignorados'], ensure_ascii=False):
        errors.append('o mapa não declara ter ignorado o .git')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
