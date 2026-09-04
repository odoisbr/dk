#!/usr/bin/env python3
"""O contrato de resposta é referenciado, nunca copiado.

Toda SKILL.md declara a forma da saída e aponta para o contrato. Nenhuma repete
o corpo dele — foi assim que o Kit anterior acumulou 48% de texto duplicado."""
from __future__ import annotations
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CONTRATO = RAIZ / 'docs' / 'contrato-de-resposta.md'
FORMAS = {'frase', 'tabela', 'documento'}

errors = []

if not CONTRATO.exists():
    errors.append('docs/contrato-de-resposta.md não existe')
    for e in errors:
        print(e)
    sys.exit(1)

corpo = CONTRATO.read_text(encoding='utf-8')
marcadores = [linha.strip() for linha in corpo.splitlines()
              if linha.startswith('## ') and linha.strip() != '## Em qualquer forma']

for skill in sorted(RAIZ.glob('skills/*/SKILL.md')):
    texto = skill.read_text(encoding='utf-8')
    fm = texto.split('---', 2)[1] if texto.startswith('---\n') else ''

    m = re.search(r'^forma-da-saida:\s*(\S+)', fm, re.M)
    if not m:
        errors.append(f'{skill.parent.name}: falta forma-da-saida no front-matter')
    elif m.group(1) not in FORMAS:
        errors.append(f'{skill.parent.name}: forma-da-saida {m.group(1)!r} inválida')

    if 'contrato-de-resposta' not in texto:
        errors.append(f'{skill.parent.name}: não referencia o contrato de resposta')

    for marcador in marcadores:
        if marcador in texto:
            errors.append(
                f'{skill.parent.name}: copia a seção {marcador!r} do contrato '
                'em vez de referenciá-la')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
