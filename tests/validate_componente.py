#!/usr/bin/env python3
"""O contrato do componente e o espelhamento das quatro camadas."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import componente, io  # noqa: E402

errors = []

SPEC = """schemaVersion: 1
id: component.alert
name: Alert
slug: alert
version: 1.0.0
status: stable
responsibility:
  description: Apresentar mensagens.
canonicalStructure:
  markup: alert.html
  style: alert.css
  behavior: alert.js
  specification: alert.yaml
variants:
  - id: info
    selector: '[data-variant="info"]'
  - id: error
    selector: '[data-variant="error"]'
states:
  - id: default
    selector: '[data-state="default"]'
"""
HTML = '<div class="alert" data-variant="info" data-state="default"></div>'
CSS = ('.alert[data-variant="info"]{color:var(--token-blue)}\n'
       '.alert[data-variant="error"]{color:var(--token-red)}\n'
       '.alert[data-state="default"]{display:block}\n')
JS = ('export class Alert{setVariant(v){this.el.dataset.variant=v}\n'
      'setState(s){this.el.dataset.state=s}}\n')


def montar(raiz: Path, slug='alert', spec=SPEC, html=HTML, css=CSS, js=JS,
           ext='.css'):
    base = raiz / 'design-system' / 'components' / slug
    if spec is not None:
        io.atomic_write(base / f'{slug}.yaml', spec)
    if html is not None:
        io.atomic_write(base / f'{slug}.html', html)
    if css is not None:
        io.atomic_write(base / f'{slug}{ext}', css)
    if js is not None:
        io.atomic_write(base / f'{slug}.js', js)
    return base


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz)
    achados = componente.verificar(raiz)
    if achados:
        errors.append(f'componente completo não deveria ter achado: {achados}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, js=None)
    ids = {a['id'] for a in componente.verificar(raiz)}
    if 'CMP-ESTRUTURA' not in ids:
        errors.append('componente sem o .js deveria reprovar a regra imutável')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = montar(raiz)
    io.atomic_write(base / 'alert.tsx', 'export const Alert = () => null')
    ids = {a['id'] for a in componente.verificar(raiz)}
    if 'CMP-FORMATO' not in ids:
        errors.append('formato de framework fora de adapters/ deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    # variação declarada no YAML e ausente do estilo
    montar(raiz, css='.alert[data-variant="info"]{}\n'
                     '.alert[data-state="default"]{}\n')
    esp = [a for a in componente.verificar(raiz) if a['id'] == 'CMP-ESPELHO']
    if not esp:
        errors.append('variação sem estilo deveria quebrar o espelhamento')
    elif 'error' not in ' '.join(a['evidencia'] for a in esp):
        errors.append(f'o espelhamento não nomeou a variação faltante: {esp}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    # estilo com variação que o YAML não declara
    montar(raiz, css=CSS + '.alert[data-variant="fantasma"]{}\n')
    esp = [a for a in componente.verificar(raiz) if a['id'] == 'CMP-ESPELHO']
    if not any('fantasma' in a['evidencia'] for a in esp):
        errors.append('variação só no estilo deveria ser apontada')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, js='export class Alert{}\n')
    esp = [a for a in componente.verificar(raiz) if a['id'] == 'CMP-ESPELHO']
    if not any('setVariant' in a['evidencia'] for a in esp):
        errors.append('YAML com variações e JS sem setVariant deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, spec=SPEC.replace('status: stable', 'status: pronto'))
    if 'CMP-STATUS' not in {a['id'] for a in componente.verificar(raiz)}:
        errors.append('status fora do enum deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, spec=SPEC.replace('slug: alert', 'slug: aviso'))
    if 'CMP-SLUG' not in {a['id'] for a in componente.verificar(raiz)}:
        errors.append('slug divergente da pasta deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    if componente.verificar(Path(d)):
        errors.append('projeto sem design-system não deveria ter achado')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    montar(raiz, ext='.scss')
    if 'CMP-ESTRUTURA' in {a['id'] for a in componente.verificar(raiz)}:
        errors.append('scss é estilo válido pelo contrato')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
