#!/usr/bin/env python3
"""O prototipar abre changeset, verifica o padrão e recusa alvo não declarado."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = raiz / '2-design' / 'prototipo'
    io.atomic_write(base / 'index.html', '<a href="/vitrine">vitrine</a>')
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:#009CC5}')

    v = dk('prototipar', '--projeto', str(raiz), '--verificar')
    if v.returncode == 0:
        errors.append('valor cru no tema deveria reprovar a verificação')
    if '14' not in v.stdout:
        errors.append('a verificação não citou a regra violada')
    if '--cor-primaria' not in v.stdout:
        errors.append('a verificação não nomeou a variável')

    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:var(--token-blue)}')
    v2 = dk('prototipar', '--projeto', str(raiz), '--verificar')
    if v2.returncode != 0:
        errors.append(f'protótipo corrigido deveria passar: {v2.stdout}')

    seco = dk('prototipar', '--projeto', str(raiz),
              '--changeset', 'CS-001', '--titulo', 'ajuste do card',
              '--origem', 'pedido em 04/09',
              '--alvo', '2-design/prototipo/styles')
    if seco.returncode != 0:
        errors.append(f'abrir changeset falhou: {seco.stdout}{seco.stderr}')
    for esperado in ('CS-001', 'affected', '2-design/prototipo/styles'):
        if esperado not in seco.stdout:
            errors.append(f'{esperado!r} ausente da saída')
    if 'simulação' not in seco.stdout:
        errors.append('sem --apply deveria simular')
    if (raiz / '.dk' / 'changesets').exists():
        errors.append('a simulação gravou o changeset')

    ap = dk('prototipar', '--projeto', str(raiz),
            '--changeset', 'CS-001', '--titulo', 'ajuste do card',
            '--origem', 'pedido em 04/09',
            '--alvo', '2-design/prototipo/styles', '--apply')
    if ap.returncode != 0:
        errors.append(f'--apply falhou: {ap.stdout}{ap.stderr}')
    if not (raiz / '.dk' / 'changesets' / 'CS-001.json').exists():
        errors.append('--apply não gravou o changeset')

    sem_alvo = dk('prototipar', '--projeto', str(raiz),
                  '--changeset', 'CS-002', '--titulo', 'x', '--origem', 'y')
    if sem_alvo.returncode == 0:
        errors.append('changeset sem alvo deveria reprovar')
    if 'CS-SEM-ALVO' not in sem_alvo.stdout:
        errors.append('a recusa não citou CS-SEM-ALVO')

    sem_origem = dk('prototipar', '--projeto', str(raiz),
                    '--changeset', 'CS-003', '--titulo', 'x', '--origem', '',
                    '--alvo', '2-design/prototipo/styles')
    if sem_origem.returncode == 0:
        errors.append('changeset sem origem deveria reprovar')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
