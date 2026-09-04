#!/usr/bin/env python3
"""Identidade visual da SEA: fonte única dos tokens.

Verificado na auditoria: o `sea_brand.py` do Kit e os tokens da skill de documento
padrão do community declaram a mesma paleta e as mesmas fontes. Aqui elas existem
uma vez, e tanto o HTML quanto o PDF consomem daqui.

As fontes vão embutidas em base64 porque o entregável precisa ser autocontido:
um HTML que depende de fonte externa quebra quando sai do computador de quem gerou."""
from __future__ import annotations
import base64
from functools import lru_cache
from pathlib import Path

MARCA = Path(__file__).resolve().parents[1] / 'templates' / 'marca'

CORES = {
    'blue': '#009CC5',
    'blue_text': '#019CC5',
    'blue_dark': '#017A9B',
    'ink': '#112428',
    'body': '#434343',
    'muted': '#666666',
    'rule': '#BFBFBF',
    'cell_border': '#D9D9D9',
    'tint_1': '#F4FAFC',
    'tint_2': '#E3F1F6',
}

FACES = (
    ('Lato', 400, 'Lato-Regular.ttf'),
    ('Lato', 700, 'Lato-Bold.ttf'),
    ('PT Sans Narrow', 700, 'PTSansNarrow-Bold.ttf'),
)

PILHA_CORPO = ('"Lato", -apple-system, BlinkMacSystemFont, "Segoe UI", '
               'Roboto, Arial, sans-serif')
PILHA_TITULO = '"PT Sans Narrow", "Lato", "Arial Narrow", Arial, sans-serif'
PILHA_MONO = ('ui-monospace, SFMono-Regular, Menlo, Consolas, '
              '"Liberation Mono", monospace')


@lru_cache(maxsize=1)
def font_faces() -> str:
    blocos = []
    for familia, peso, arquivo in FACES:
        caminho = MARCA / 'fonts' / arquivo
        if not caminho.exists():
            continue
        dados = base64.b64encode(caminho.read_bytes()).decode('ascii')
        blocos.append(
            '@font-face{'
            f'font-family:"{familia}";font-weight:{peso};font-style:normal;'
            'font-display:swap;'
            f'src:url(data:font/ttf;base64,{dados}) format("truetype");'
            '}')
    return '\n'.join(blocos)


@lru_cache(maxsize=2)
def logo_svg(branca: bool = True) -> str:
    caminho = MARCA / ('sea-logo-branco.svg' if branca else 'sea-logo.svg')
    if not caminho.exists():
        caminho = MARCA / 'sea-logo-branco.svg'
    return caminho.read_text(encoding='utf-8') if caminho.exists() else ''
