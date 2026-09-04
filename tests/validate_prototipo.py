#!/usr/bin/env python3
"""As regras que dizem o que é fugir do padrão, verificadas por código."""
from __future__ import annotations
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, prototipo  # noqa: E402

errors = []


def projeto_limpo(raiz: Path) -> Path:
    base = raiz / '2-design' / 'prototipo'
    io.atomic_write(base / 'index.html', '<a href="/vitrine">vitrine</a>')
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:var(--token-blue)}')
    return base


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    projeto_limpo(raiz)
    achados = prototipo.verificar(raiz)
    if achados:
        errors.append(f'protótipo limpo não deveria ter achado: {achados}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'vendor' / 'design-system' / 'ds.css', '.x{}')
    if 7 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('cópia vendorizada de design system deveria reprovar (7)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = raiz / '2-design' / 'prototipo'
    io.atomic_write(base / 'index.html', '<p>sem rota</p>')
    io.atomic_write(base / 'styles' / 'tema.css', ':root{--a:var(--b)}')
    if 8 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('protótipo sem rota de vitrine deveria reprovar (8)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'index.html',
                    '<link href="bootstrap.min.css"><a href="/vitrine">v</a>')
    if 12 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('framework CSS concorrente deveria reprovar (12)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'index.html',
                    '<div data-bs-toggle="modal"></div><a href="/vitrine">v</a>')
    if 13 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('API exclusiva do Bootstrap 5 deveria reprovar (13)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:#009CC5;--espaco:12px}')
    achados = [a for a in prototipo.verificar(raiz) if a['regra'] == 14]
    if not achados:
        errors.append('variável de tema com valor cru deveria reprovar (14)')
    elif '--cor-primaria' not in achados[0]['evidencia']:
        errors.append(f"a evidência não nomeia a variável: {achados[0]['evidencia']}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    fonte = base / 'styles' / 'tema.scss'
    saida = base / 'styles' / 'tema.css'
    io.atomic_write(saida, ':root{--a:var(--b)}')
    io.atomic_write(fonte, '// fonte mais nova')
    agora = time.time()
    os.utime(saida, (agora - 60, agora - 60))
    os.utime(fonte, (agora, agora))
    if 15 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('saída compilada mais velha que a fonte deveria reprovar (15)')

with tempfile.TemporaryDirectory() as d:
    if prototipo.verificar(Path(d)):
        errors.append('projeto sem protótipo não deveria ter achado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
