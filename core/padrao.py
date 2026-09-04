#!/usr/bin/env python3
"""Estrutura canônica do projeto de design, portada do padrão do Kit.

`sea-design-template@2`: apoio recebe o que vem de fora, levantamento guarda o
markdown da fase, design guarda protótipo e styleguide, entregáveis guarda só o
PDF consolidado — saída gerada, nunca editada à mão.

As regras aqui são as que a estrutura permite verificar. As de protótipo e CSS
entram com o módulo de protótipo, onde há o que verificar."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

PASTAS = (
    '0-apoio',
    '1-levantamento',
    '1-levantamento/pesquisa',
    '1-levantamento/visao',
    '1-levantamento/requisitos',
    '1-levantamento/qualidade',
    '1-levantamento/atas',
    '1-levantamento/briefing',
    '1-levantamento/fluxos',
    '2-design',
    '3-entregaveis',
    'registry',
)

# chave → (pasta de destino, obrigatório no núcleo)
ENTREGAVEIS: Dict[str, tuple] = {
    'briefing': ('1-levantamento/briefing', True),
    'visao': ('1-levantamento/visao', True),
    'visao-produto': ('1-levantamento/visao', False),
    'escopo-comentado': ('1-levantamento/visao', True),
    'requisitos': ('1-levantamento/requisitos', True),
    'fluxos': ('1-levantamento/fluxos', True),
    'mc': ('1-levantamento/qualidade', True),
    'ata': ('1-levantamento/atas', True),
    'pendencias': ('registry', True),
    'historico': ('registry', True),
    'prototipo': ('2-design', True),
    'handoff': ('2-design', True),
}

# minúsculas, hífen, sem espaço e sem versão solta no nome
_CONVENCAO = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+$')
_EXCECOES = {'README.md', 'GUIA.md', 'CHANGELOG.md'}


def destino(chave: str) -> str:
    return ENTREGAVEIS[chave][0]


def verificar(raiz: Path) -> List[dict]:
    """Devolve os achados. Lista vazia é projeto em conformidade estrutural."""
    raiz = Path(raiz)
    achados = []

    faltando = [p for p in PASTAS if not (raiz / p).is_dir()]
    if faltando:
        achados.append({
            'regra': 1,
            'titulo': 'Pastas obrigatórias presentes',
            'evidencia': 'ausentes: ' + ', '.join(faltando),
            'impacto': 'alto',
        })

    for chave, (pasta, obrigatorio) in sorted(ENTREGAVEIS.items()):
        alvo = raiz / pasta
        if not obrigatorio or not alvo.is_dir():
            continue
        if not any(alvo.iterdir()):
            achados.append({
                'regra': 2,
                'titulo': 'Nome canônico dos entregáveis',
                'evidencia': f'{pasta}/ vazia — entregável "{chave}" sem arquivo',
                'impacto': 'medio',
            })

    for p in sorted(raiz.rglob('*.md')):
        rel = p.relative_to(raiz)
        if any(parte.startswith('.') for parte in rel.parts):
            continue
        if p.name in _EXCECOES:
            continue
        if not _CONVENCAO.match(p.name):
            achados.append({
                'regra': 3,
                'titulo': 'Convenção de nomes',
                'evidencia': f'{rel}: fora do padrão minúsculas-com-hífen',
                'impacto': 'baixo',
            })

    apoio = raiz / '0-apoio' / 'reunioes'
    atas = raiz / '1-levantamento' / 'atas'
    if apoio.is_dir() and atas.is_dir():
        insumos = list(apoio.glob('*.md')) + list(apoio.glob('*.txt'))
        if insumos and not any(atas.iterdir()):
            achados.append({
                'regra': 4,
                'titulo': 'Insumo × entregável',
                'evidencia': f'{len(insumos)} insumo(s) em 0-apoio/reunioes/ '
                             'sem ata correspondente em 1-levantamento/atas/',
                'impacto': 'alto',
            })

    for chave in ('visao', 'requisitos'):
        pasta = raiz / destino(chave)
        if not pasta.is_dir():
            continue
        for doc in sorted(pasta.glob('*.md')):
            texto = doc.read_text(encoding='utf-8', errors='replace')
            if 'Validação e Aprovação' not in texto:
                achados.append({
                    'regra': 6,
                    'titulo': 'Bloco "Validação e Aprovação" em Visão e Requisitos',
                    'evidencia': f'{doc.relative_to(raiz)}: bloco ausente',
                    'impacto': 'medio',
                })

    return achados
