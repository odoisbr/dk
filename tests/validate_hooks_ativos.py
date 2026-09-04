#!/usr/bin/env python3
"""O hook existe, é executável, e o clone está configurado para usá-lo.

Hook que depende de um `git config` manual que ninguém roda é hook desligado."""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []

hook = RAIZ / '.githooks' / 'pre-push'
if not hook.exists():
    errors.append('.githooks/pre-push não existe')
elif not os.access(hook, os.X_OK):
    errors.append('.githooks/pre-push não é executável')

instalador = RAIZ / 'bin' / 'dk-instalar-hooks'
if not instalador.exists():
    errors.append('bin/dk-instalar-hooks não existe')

r = subprocess.run(['git', 'config', 'core.hooksPath'],
                   cwd=str(RAIZ), capture_output=True, text=True)
configurado = r.stdout.strip()
if configurado != '.githooks':
    errors.append(
        f'core.hooksPath é {configurado!r}, esperado ".githooks" — '
        'rode bin/dk-instalar-hooks')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
