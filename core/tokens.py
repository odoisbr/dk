#!/usr/bin/env python3
"""Tokens no formato DTCG, portado do `sea-dls`.

O arquivo é uma árvore; folha é o objeto que tem `$value`. Cada folha declara
`$type` de um conjunto fechado — o mesmo do W3C Design Tokens.

Duas verificações, e a segunda é a que aparece tarde demais quando não existe:

**Folha malformada** — sem `$value` ou com `$type` fora do conjunto. Erra na
geração, e a mensagem costuma não dizer qual token.

**Referência não resolvida** — `{cor.primaria}` apontando para um token que não
existe. Isso não quebra o build: gera CSS com a chave literal dentro, e a cor
simplesmente não aplica. É o defeito que passa por revisão visual porque só se
manifesta no navegador de alguém."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

TIPOS = ('color', 'dimension', 'shadow', 'typography', 'duration',
         'cubicBezier', 'number', 'fontFamily', 'fontWeight')

ARQUIVO = 'design-system/tokens.json'
_REFERENCIA = re.compile(r'\{([^}]+)\}')


def _achado(ident, caminho, titulo, evidencia, impacto='medio') -> Dict:
    return {'id': ident, 'token': caminho, 'titulo': titulo,
            'evidencia': evidencia, 'impacto': impacto}


def folhas(arvore, prefixo: str = '') -> List[Tuple[str, dict]]:
    """Todo nó com `$value` é folha; o resto é galho. Devolve (caminho, folha)."""
    saida = []
    if not isinstance(arvore, dict):
        return saida
    if '$value' in arvore:
        return [(prefixo, arvore)]
    for chave, valor in arvore.items():
        if chave.startswith('$'):
            continue
        caminho = f'{prefixo}.{chave}' if prefixo else chave
        saida.extend(folhas(valor, caminho))
    return saida


def verificar(raiz: Path, arquivo: str = ARQUIVO) -> List[Dict]:
    alvo = Path(raiz) / arquivo
    if not alvo.exists():
        return []
    try:
        arvore = json.loads(alvo.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return [_achado('TOK-JSON', arquivo, 'tokens.json não é JSON válido',
                        f'{arquivo}: {exc}', 'alto')]

    todas = folhas(arvore)
    nomes = {caminho for caminho, _ in todas}
    achados = []

    for caminho, folha in todas:
        if '$type' not in folha:
            achados.append(_achado(
                'TOK-SEM-TIPO', caminho, 'token sem $type',
                f'{caminho}: DTCG exige $value e $type', 'alto'))
        elif folha['$type'] not in TIPOS:
            achados.append(_achado(
                'TOK-TIPO', caminho, '$type fora do conjunto',
                f"{caminho}: $type {folha['$type']!r}; válidos: "
                + ', '.join(TIPOS), 'alto'))

        valor = folha.get('$value')
        if isinstance(valor, str):
            for referencia in _REFERENCIA.findall(valor):
                if referencia not in nomes:
                    achados.append(_achado(
                        'TOK-REFERENCIA', caminho,
                        'referência não resolvida',
                        f'{caminho} aponta para {{{referencia}}}, que não existe '
                        '— o build não quebra; a chave sai literal no CSS e o '
                        'estilo não aplica',
                        'alto'))

    if not todas:
        achados.append(_achado(
            'TOK-VAZIO', arquivo, 'nenhum token declarado',
            f'{arquivo} existe e não tem nenhuma folha com $value'))

    return achados
