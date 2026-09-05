#!/usr/bin/env python3
"""Contrato do componente canônico, portado do `sea-dls`.

Duas coisas são verificadas, e a segunda é a que não dá para fazer à mão.

**A regra imutável.** Todo componente é quatro arquivos com o mesmo nome:

    <slug>/
      <slug>.html          sempre .html
      <slug>.css|.scss     só o estilo é configurável
      <slug>.js            sempre .js
      <slug>.yaml          a especificação

Formato de framework — `.tsx`, `.vue`, `.component.ts` — existe apenas como
derivado em `adapters/<target>/`, apontando para o YAML. Vale para qualquer
stack, e é o que impede o componente virar cinco componentes diferentes.

**O espelhamento das quatro camadas.** Variação e estado precisam aparecer nas
quatro, e com o mesmo nome:

    HTML   data-variant="info"        data-state="loading"
    CSS    [data-variant="info"]      [data-state="loading"]
    JS     setVariant("info")         setState("loading")
    YAML   variants: [{id: info}]     states: [{id: loading}]

Um lado sem os outros é divergência. Conferir isso à mão em vinte componentes é
o tipo de trabalho que ninguém faz duas vezes — e é determinístico."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

from core import miniyaml

STATUS = ('draft', 'experimental', 'stable', 'deprecated')
OBRIGATORIOS = ('schemaVersion', 'id', 'name', 'slug', 'version', 'status',
                'responsibility', 'canonicalStructure', 'variants', 'states')
ESTILOS = ('.css', '.scss')

_DATA_VARIANT = re.compile(r'data-variant\s*=\s*["\']([\w-]+)["\']')
_DATA_STATE = re.compile(r'data-state\s*=\s*["\']([\w-]+)["\']')
_SEL_VARIANT = re.compile(r'\[data-variant\s*=\s*["\']([\w-]+)["\']\]')
_SEL_STATE = re.compile(r'\[data-state\s*=\s*["\']([\w-]+)["\']\]')


def _achado(ident, componente, titulo, evidencia, impacto='medio') -> Dict:
    return {'id': ident, 'componente': componente, 'titulo': titulo,
            'evidencia': evidencia, 'impacto': impacto}


def _ler(caminho: Path) -> str:
    return caminho.read_text(encoding='utf-8', errors='replace') \
        if caminho.exists() else ''


def verificar_um(pasta: Path) -> List[Dict]:
    slug = pasta.name
    achados = []

    spec = pasta / f'{slug}.yaml'
    html = pasta / f'{slug}.html'
    js = pasta / f'{slug}.js'
    estilos = [pasta / f'{slug}{e}' for e in ESTILOS]
    estilo = next((e for e in estilos if e.exists()), None)

    faltando = []
    if not spec.exists():
        faltando.append(f'{slug}.yaml')
    if not html.exists():
        faltando.append(f'{slug}.html')
    if not js.exists():
        faltando.append(f'{slug}.js')
    if estilo is None:
        faltando.append(f'{slug}.css ou {slug}.scss')
    if faltando:
        achados.append(_achado(
            'CMP-ESTRUTURA', slug, 'regra imutável do componente',
            f'{slug}/: faltam ' + ', '.join(faltando)
            + ' — o componente é quatro arquivos com o mesmo nome',
            'alto'))

    estranhos = [p.name for p in sorted(pasta.iterdir())
                 if p.is_file() and p.suffix in ('.tsx', '.vue', '.jsx', '.ts')]
    if estranhos:
        achados.append(_achado(
            'CMP-FORMATO', slug, 'formato de framework fora de adapters/',
            f'{slug}/: {", ".join(estranhos)} — formato de framework existe só '
            'como derivado em adapters/<target>/, apontando para o YAML',
            'alto'))

    if not spec.exists():
        return achados

    try:
        dados = miniyaml.carregar(_ler(spec))
    except miniyaml.YamlNaoSuportado as exc:
        return achados + [_achado('CMP-YAML', slug,
                                  'especificação não pôde ser lida',
                                  f'{slug}.yaml: {exc}', 'alto')]
    if not isinstance(dados, dict):
        return achados + [_achado('CMP-YAML', slug,
                                  'especificação não é um mapa',
                                  f'{slug}.yaml: raiz é {type(dados).__name__}',
                                  'alto')]

    ausentes = [c for c in OBRIGATORIOS if not dados.get(c)]
    if ausentes:
        achados.append(_achado(
            'CMP-CAMPO', slug, 'campo obrigatório do contrato ausente',
            f'{slug}.yaml: faltam ' + ', '.join(ausentes), 'alto'))
    if dados.get('status') and dados['status'] not in STATUS:
        achados.append(_achado(
            'CMP-STATUS', slug, 'status fora do contrato',
            f"{slug}.yaml: status {dados['status']!r}; válidos: "
            + ', '.join(STATUS)))
    if dados.get('slug') and dados['slug'] != slug:
        achados.append(_achado(
            'CMP-SLUG', slug, 'slug divergente da pasta',
            f"{slug}.yaml declara slug {dados['slug']!r}", 'alto'))

    # ── o espelhamento das quatro camadas ──
    texto_html, texto_estilo = _ler(html), _ler(estilo) if estilo else ''
    texto_js = _ler(js)

    for rotulo, chave, re_html, re_css, metodo in (
            ('variação', 'variants', _DATA_VARIANT, _SEL_VARIANT, 'setVariant'),
            ('estado', 'states', _DATA_STATE, _SEL_STATE, 'setState')):
        no_yaml = {str(v.get('id')) for v in (dados.get(chave) or [])
                   if isinstance(v, dict) and v.get('id')}
        no_html = set(re_html.findall(texto_html))
        no_css = set(re_css.findall(texto_estilo))
        declara_js = bool(re.search(rf'\b{metodo}\b', texto_js))

        for ident in sorted(no_yaml - no_css):
            achados.append(_achado(
                'CMP-ESPELHO', slug, f'{rotulo} sem estilo',
                f'{slug}.yaml declara {rotulo} {ident!r} e o estilo não tem '
                f'[data-{"variant" if chave == "variants" else "state"}="{ident}"]'))
        for ident in sorted(no_css - no_yaml):
            achados.append(_achado(
                'CMP-ESPELHO', slug, f'{rotulo} só no estilo',
                f'o estilo tem {ident!r} e o {slug}.yaml não declara — '
                'especificação é a fonte, estilo é consumidor'))
        for ident in sorted(no_html - no_yaml):
            achados.append(_achado(
                'CMP-ESPELHO', slug, f'{rotulo} só no markup',
                f'{slug}.html usa {ident!r} e o {slug}.yaml não declara'))
        if no_yaml and not declara_js:
            achados.append(_achado(
                'CMP-ESPELHO', slug, f'{rotulo} sem comportamento',
                f'{slug}.yaml declara {len(no_yaml)} {rotulo}(ões) e '
                f'{slug}.js não expõe {metodo}()'))

    return achados


def verificar(raiz: Path, base: str = 'design-system/components') -> List[Dict]:
    pasta = Path(raiz) / base
    if not pasta.is_dir():
        return []
    achados = []
    for componente in sorted(p for p in pasta.iterdir() if p.is_dir()):
        achados.extend(verificar_um(componente))
    return achados
