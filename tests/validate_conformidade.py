#!/usr/bin/env python3
"""O auditor responde: este projeto usa DK? em que estado?"""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import conformidade, scan  # noqa: E402

errors = []
VALIDAS = {'COMPATIVEL', 'PARCIALMENTE COMPATIVEL', 'DESATUALIZADO',
           'INCONSISTENTE', 'NAO COMPATIVEL'}

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'src').mkdir()
    (raiz / 'src' / 'a.js').write_text('x\n', encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if r['usa_dk']:
        errors.append('projeto sem artefato DK marcado como usuário de DK')
    if r['classificacao'] != 'NAO COMPATIVEL':
        errors.append(f"esperado NAO COMPATIVEL, veio {r['classificacao']}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'registry').mkdir()
    (raiz / 'registry' / 'requisitos.json').write_text('[]', encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if not r['usa_dk']:
        errors.append('registry/ presente e não reconheceu uso de DK')
    if r['classificacao'] not in VALIDAS:
        errors.append(f"classificação inválida: {r['classificacao']}")
    if r['classificacao'] == 'COMPATIVEL':
        errors.append('projeto só com registry não deveria ser COMPATIVEL')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for sub in ('registry', '0-apoio', 'docs'):
        (raiz / sub).mkdir()
    (raiz / 'registry' / 'requisitos.json').write_text('[]', encoding='utf-8')
    (raiz / 'registry' / 'regras.json').write_text('[]', encoding='utf-8')
    (raiz / 'projeto.yml').write_text('nome: x\n', encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if r['classificacao'] != 'COMPATIVEL':
        errors.append(f"projeto com núcleo completo veio {r['classificacao']}")
    if not r['artefatos']:
        errors.append('nenhum artefato listado')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'registry').mkdir()
    (raiz / 'registry' / 'requisitos.json').write_text('nao e json',
                                                       encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if r['classificacao'] != 'INCONSISTENTE':
        errors.append(f"registry quebrado deveria dar INCONSISTENTE, "
                      f"veio {r['classificacao']}")
    if not r['achados']:
        errors.append('inconsistência sem achado descrito')
    for a in r['achados']:
        if not a.get('evidencia'):
            errors.append(f'achado sem evidência: {a}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
