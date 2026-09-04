#!/usr/bin/env python3
"""Os tokens da marca são os reais, não inventados.

Os valores abaixo foram lidos do sea_brand.py do Kit e dos tokens declarados na
skill criar-documento-padrao do community — as duas linhagens já concordavam."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import marca  # noqa: E402

errors = []

ESPERADAS = {
    'blue': '#009CC5', 'blue_text': '#019CC5', 'ink': '#112428',
    'body': '#434343', 'muted': '#666666', 'rule': '#BFBFBF',
    'cell_border': '#D9D9D9',
}
for chave, valor in ESPERADAS.items():
    if marca.CORES.get(chave) != valor:
        errors.append(f'CORES[{chave!r}] = {marca.CORES.get(chave)!r}, '
                      f'esperado {valor!r}')

if 'Lato' not in marca.PILHA_CORPO:
    errors.append('a pilha de corpo deveria começar em Lato')
if 'PT Sans Narrow' not in marca.PILHA_TITULO:
    errors.append('a pilha de título deveria começar em PT Sans Narrow')

faces = marca.font_faces()
if '@font-face' not in faces:
    errors.append('font_faces() não emite @font-face')
if 'base64' not in faces:
    errors.append('as fontes precisam ir embutidas: o HTML é autocontido')
if faces.count('@font-face') != len(marca.FACES):
    errors.append(f'{faces.count("@font-face")} faces emitidas para '
                  f'{len(marca.FACES)} declaradas')

if '<svg' not in marca.logo_svg():
    errors.append('logo_svg() não devolveu SVG')

for ativo in ('templates/marca/fonts/Lato-Regular.ttf',
              'templates/marca/fonts/Lato-Bold.ttf',
              'templates/marca/fonts/PTSansNarrow-Bold.ttf',
              'templates/marca/sea-logo-branco.svg'):
    if not (RAIZ / ativo).exists():
        errors.append(f'{ativo} ausente')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
