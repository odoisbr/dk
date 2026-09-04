#!/usr/bin/env python3
"""O audit roda, simula por padrão, e o llms.txt que ele propõe é derivado do mapa."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'src').mkdir()
    (raiz / 'package.json').write_text(
        json.dumps({'name': 'demo', 'dependencies': {'react': '^18'}}),
        encoding='utf-8')
    (raiz / 'README.md').write_text('# demo\n', encoding='utf-8')
    (raiz / 'src' / 'index.js').write_text('export default 1\n', encoding='utf-8')

    seco = dk('audit', '--projeto', str(raiz))
    if seco.returncode != 0:
        errors.append(f'audit falhou: {seco.stdout}{seco.stderr}')
    if (raiz / '.dk' / 'mapa.json').exists():
        errors.append('a simulação gravou o mapa')
    if (raiz / 'llms.txt').exists():
        errors.append('a simulação gravou o llms.txt')
    for esperado in ('react', 'NAO COMPATIVEL', 'estimativa'):
        if esperado not in seco.stdout:
            errors.append(f'{esperado!r} ausente da saída do audit')

    j = dk('audit', '--projeto', str(raiz), '--json')
    if j.returncode != 0:
        errors.append(f'audit --json falhou: {j.stderr}')
    else:
        try:
            dados = json.loads(j.stdout)
        except json.JSONDecodeError as exc:
            dados = {}
            errors.append(f'--json não emitiu JSON: {exc}')
        for chave in ('projeto', 'metricas', 'conformidade', 'importantes'):
            if chave not in dados:
                errors.append(f'--json sem a chave {chave}')

    ap = dk('audit', '--projeto', str(raiz), '--apply')
    if ap.returncode != 0:
        errors.append(f'audit --apply falhou: {ap.stdout}{ap.stderr}')
    if not (raiz / '.dk' / 'mapa.json').exists():
        errors.append('--apply não gravou .dk/mapa.json')
    if not (raiz / 'llms.txt').exists():
        errors.append('--apply não gravou llms.txt')
    else:
        texto = (raiz / 'llms.txt').read_text(encoding='utf-8')
        if 'react' not in texto:
            errors.append('o llms.txt não reflete a stack detectada')
        if 'README.md' not in texto:
            errors.append('o llms.txt não aponta os documentos do projeto')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
