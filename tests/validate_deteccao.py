#!/usr/bin/env python3
"""Stack sai de evidência de arquivo, nunca de nome de diretório."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import deteccao, scan  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'package.json').write_text(json.dumps({
        'name': 'app', 'dependencies': {'react': '^18', 'next': '^14'},
    }), encoding='utf-8')
    (raiz / 'pnpm-lock.yaml').write_text('lockfileVersion: 6\n', encoding='utf-8')
    (raiz / 'backend').mkdir()

    r = deteccao.detectar(raiz, scan.varrer(raiz))
    if 'react' not in r['stack']:
        errors.append(f"react não detectado: {r['stack']}")
    if 'next' not in r['stack']:
        errors.append(f"next não detectado: {r['stack']}")
    if r['gerenciador'] != 'pnpm':
        errors.append(f"gerenciador errado: {r['gerenciador']}")
    if 'backend' in r['stack']:
        errors.append('detectou backend por nome de diretório, não por evidência')
    if not r['evidencias']:
        errors.append('nenhuma evidência citada')
    for ev in r['evidencias']:
        if not (raiz / ev.split(':')[0]).exists():
            errors.append(f'evidência aponta para arquivo inexistente: {ev}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'pyproject.toml').write_text(
        '[project]\nname = "x"\ndependencies = ["fastapi"]\n', encoding='utf-8')
    r = deteccao.detectar(raiz, scan.varrer(raiz))
    if 'python' not in r['stack']:
        errors.append(f"python não detectado: {r['stack']}")
    if 'fastapi' not in r['stack']:
        errors.append(f"fastapi não detectado: {r['stack']}")
    if r['tipo'] != 'backend':
        errors.append(f"projeto fastapi deveria ser backend, veio {r['tipo']}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / '.claude-plugin').mkdir()
    (raiz / '.claude-plugin' / 'plugin.json').write_text('{"name":"x"}',
                                                        encoding='utf-8')
    r = deteccao.detectar(raiz, scan.varrer(raiz))
    if r['tipo'] != 'plugin':
        errors.append(f"tipo esperado plugin, veio {r['tipo']}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
