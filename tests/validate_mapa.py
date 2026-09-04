#!/usr/bin/env python3
"""O mapa é progressivo, ranqueado, e declara o que não olhou."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import mapa  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'src').mkdir()
    (raiz / 'node_modules').mkdir()
    (raiz / 'node_modules' / 'a.js').write_text('x\n', encoding='utf-8')
    (raiz / 'package.json').write_text(json.dumps({'name': 'x'}), encoding='utf-8')
    (raiz / 'README.md').write_text('# x\n' * 50, encoding='utf-8')
    (raiz / 'src' / 'index.js').write_text('export default 1\n', encoding='utf-8')
    (raiz / 'src' / 'util.js').write_text('const a = 1\n', encoding='utf-8')

    m0 = mapa.montar(raiz, nivel=0)
    if m0['importantes']:
        errors.append('nível 0 não deveria ranquear')
    if not m0['metricas'].get('arquivos'):
        errors.append('nível 0 deveria contar arquivos')

    m1 = mapa.montar(raiz, nivel=1)
    if not m1['estrutura']:
        errors.append('nível 1 deveria classificar por tipo')
    if m1['importantes']:
        errors.append('nível 1 ainda não ranqueia')

    m = mapa.montar(raiz, nivel=2)
    if 'package.json' not in m['configs']:
        errors.append(f"package.json fora dos configs: {m['configs']}")
    if 'README.md' not in m['documentos']:
        errors.append(f"README fora dos documentos: {m['documentos']}")
    if 'src/index.js' not in m['entrypoints']:
        errors.append(f"index.js fora dos entrypoints: {m['entrypoints']}")

    nomes = [i['caminho'] for i in m['importantes']]
    if 'package.json' not in nomes:
        errors.append('manifesto deveria ser importante')
    if not [i for i in m['importantes'] if i['importancia'] == 'ALTA']:
        errors.append('nenhum arquivo classificado como ALTA')
    for i in m['importantes']:
        if not i.get('motivo'):
            errors.append(f"{i['caminho']}: importância sem motivo")

    if not m['ignorados']:
        errors.append('o mapa não declara o que ignorou')
    if not any('node_modules' in motivo for motivo in m['ignorados']):
        errors.append(f"node_modules não aparece nos ignorados: {m['ignorados']}")
    if m['metricas']['tokens_estimados_total'] <= 0:
        errors.append('métrica de token vazia')
    if 'estimativa' not in json.dumps(m['metricas'], ensure_ascii=False).lower():
        errors.append('a métrica de token não se declara estimativa')
    if m['metricas']['arquivos'] != 4:
        errors.append(f"esperados 4 arquivos mapeados, veio {m['metricas']['arquivos']}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
