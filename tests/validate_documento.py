#!/usr/bin/env python3
"""O HTML canônico: autocontido, com a marca, e com tabela de verdade."""
from __future__ import annotations
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import documento, marca  # noqa: E402

errors = []

CORPO = """## 1. Identificação

| Campo | Valor |
|---|---|
| Projeto | Convênios |
| Cliente | Sesc-DF |

## 2. Participantes

Texto com **negrito** e `código`.

- item um
- item dois
"""

html = documento.montar('Ata de Reunião', 'Convênios — Sesc-DF', CORPO,
                        {'cliente': 'Sesc-DF', 'data': '14/08/2026'})

if '<!doctype html>' not in html.lower():
    errors.append('sem doctype')
if 'Ata de Reunião' not in html:
    errors.append('título ausente')
if 'Convênios — Sesc-DF' not in html:
    errors.append('subtítulo ausente')
if marca.CORES['blue_text'] not in html:
    errors.append('a cor de título da marca não foi aplicada')
if '@font-face' not in html:
    errors.append('as fontes não foram embutidas')

# autocontido: nenhuma requisição de rede. Namespace de SVG não conta.
externas = re.findall(r'(?:src|href)\s*=\s*"https?://|url\(\s*["\']?https?://', html)
if externas:
    errors.append(f'o documento faz {len(externas)} requisição(ões) externa(s)')

if '<table' not in html:
    errors.append('a tabela markdown não virou <table>')
if '<th' not in html:
    errors.append('tabela sem cabeçalho')
if html.count('<td') != 4:
    errors.append(f'esperadas 4 células, vieram {html.count("<td")}')
if '<strong>negrito</strong>' not in html:
    errors.append('negrito não convertido')
if '<code>código</code>' not in html:
    errors.append('código inline não convertido')
if '<ul>' not in html or html.count('<li>') != 2:
    errors.append('lista não convertida')
if '<h2' not in html:
    errors.append('cabeçalho de seção não convertido')

escapado = documento.markdown_para_html('a < b & c')
if '&lt;' not in escapado or '&amp;' not in escapado:
    errors.append('HTML não escapado — risco de quebrar o documento')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
