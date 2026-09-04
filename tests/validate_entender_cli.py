#!/usr/bin/env python3
"""O entender roda os três, num relatório só, e não escreve nada."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import padrao, registry  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [{'id': 'RN-001', 'enunciado': 'o gestor revoga'}])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'a tela deve ser rápida', 'deriva_de': 'RN-001'},
        {'id': 'REQ-002', 'titulo': 'sem âncora', 'deriva_de': 'RN-404'},
    ])

    antes = sorted(str(p.relative_to(raiz)) for p in raiz.rglob('*') if p.is_file())
    r = dk('entender', '--projeto', str(raiz))
    if r.returncode != 0:
        errors.append(f'entender falhou: {r.stdout}{r.stderr}')
    depois = sorted(str(p.relative_to(raiz)) for p in raiz.rglob('*') if p.is_file())
    if antes != depois:
        errors.append('entender escreveu no projeto; deveria ser só leitura')

    for esperado in ('ORFAO', 'NF-SEM-CRITERIO', 'AUSENTE', 'cobertura'):
        if esperado not in r.stdout:
            errors.append(f'{esperado!r} ausente do relatório')

    j = dk('entender', '--projeto', str(raiz), '--json')
    if j.returncode != 0:
        errors.append(f'--json falhou: {j.stderr}')
    else:
        dados = json.loads(j.stdout)
        for chave in ('cobertura', 'consistencia', 'lacunas'):
            if chave not in dados:
                errors.append(f'--json sem a chave {chave}')
        if not dados['consistencia']:
            errors.append('nenhuma inconsistência num conjunto que tem duas')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
