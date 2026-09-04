#!/usr/bin/env python3
"""O leitor de YAML lê o que o contrato usa e recusa o que não entende."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import miniyaml  # noqa: E402

errors = []

SPEC = """# especificação canônica
schemaVersion: 1
id: component.alert
name: Alert
slug: alert
version: 1.0.0
status: stable

responsibility:
  description: Apresentar mensagens de contexto.

canonicalStructure:
  markup: alert.html
  style: alert.css
  behavior: alert.js
  specification: alert.yaml

variants:
  - id: info
    selector: '[data-variant="info"]'
    description: Mensagem informativa.
  - id: error
    selector: '[data-variant="error"]'

states:
  - id: default
    selector: '[data-state="default"]'
  - id: loading
    selector: '[data-state="loading"]'

properties:
  - name: message
    type: string
    required: true
"""

d = miniyaml.carregar(SPEC)

if d.get('schemaVersion') != 1:
    errors.append(f"schemaVersion inteiro esperado, veio {d.get('schemaVersion')!r}")
if d.get('slug') != 'alert':
    errors.append(f"slug: {d.get('slug')!r}")
if d.get('version') != '1.0.0':
    errors.append(f'versão virou número: {d.get("version")!r}')
if d.get('canonicalStructure', {}).get('markup') != 'alert.html':
    errors.append(f"mapa aninhado: {d.get('canonicalStructure')}")
if len(d.get('variants') or []) != 2:
    errors.append(f"variants: {d.get('variants')}")
elif d['variants'][0].get('selector') != '[data-variant="info"]':
    errors.append(f"seletor com aspas: {d['variants'][0]}")
if len(d.get('states') or []) != 2:
    errors.append(f"states: {d.get('states')}")
if (d.get('properties') or [{}])[0].get('required') is not True:
    errors.append('booleano não convertido')

if miniyaml.carregar('') != {}:
    errors.append('texto vazio deveria dar mapa vazio')

# o que não entende, recusa dizendo a linha
for fora, rotulo in (('a: &ancora x\n', 'âncora'),
                     ('a: |\n  bloco literal\n', 'bloco literal'),
                     ('---\na: 1\n', 'multi-documento')):
    try:
        miniyaml.carregar(fora)
    except miniyaml.YamlNaoSuportado as exc:
        if 'linha' not in str(exc):
            errors.append(f'{rotulo}: a recusa não diz a linha')
    else:
        errors.append(f'{rotulo} deveria ser recusado, não adivinhado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
