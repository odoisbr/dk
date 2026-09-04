#!/usr/bin/env python3
"""Changeset: o que vai mudar, declarado antes de mudar.

Modelo portado do `sea-dls`. O campo que importa é `affected` — ele vira o escopo
do envelope de escrita, e o envelope recusa qualquer caminho fora dele.

É a resposta direta à dor relatada: pediram ajuste numa tela e a ferramenta
alterou outras três. Aqui isso não é uma questão de disciplina do agente; é uma
exceção em tempo de execução."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

from core import ops

CAMPOS = ('id', 'title', 'status', 'source', 'affected', 'validation', 'result')


def abrir(ident: str, titulo: str, origem: str, afetados: List[str]) -> Dict:
    return {
        'id': ident,
        'title': titulo,
        'status': 'aberto',
        'source': origem,
        'affected': list(afetados),
        'validation': [],
        'result': '',
        'escritos': [],
    }


def validar(cs: Dict) -> List[Dict]:
    achados = []
    if not cs.get('affected'):
        achados.append({
            'id': 'CS-SEM-ALVO',
            'titulo': 'changeset sem alvo declarado',
            'evidencia': f"{cs.get('id')}: `affected` vazio — sem alvo não há "
                         'escopo, e sem escopo a escrita não é contida',
            'impacto': 'alto',
        })
    if not str(cs.get('source') or '').strip():
        achados.append({
            'id': 'CS-SEM-ORIGEM',
            'titulo': 'changeset sem origem',
            'evidencia': f"{cs.get('id')}: `source` vazio — mudança sem pedido "
                         'rastreável é mudança que ninguém pediu',
            'impacto': 'alto',
        })
    if not str(cs.get('title') or '').strip():
        achados.append({
            'id': 'CS-SEM-TITULO',
            'titulo': 'changeset sem título',
            'evidencia': f"{cs.get('id')}: `title` vazio",
            'impacto': 'medio',
        })
    return achados


def operacao(raiz: Path, cs: Dict, registro=None) -> ops.Operacao:
    """O envelope de escrita da mudança. `affected` é o escopo, sem exceção."""
    return ops.Operacao(raiz, escopo=cs['affected'], registro=registro,
                        fontes=cs.get('fontes') or [])


def fechar(cs: Dict, resultado: str, escritos: List[Path]) -> Dict:
    fechado = dict(cs)
    fechado['status'] = 'fechado'
    fechado['result'] = resultado
    fechado['escritos'] = [str(p) for p in escritos]
    return fechado
