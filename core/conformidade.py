#!/usr/bin/env python3
"""O projeto segue o modelo DK? E em que estado?

Classificação com cinco estados. `INCONSISTENTE` ganha de todos os outros: um
registro que não abre é pior que um registro que falta, porque quem lê acha que
tem informação e não tem."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

ARTEFATOS = {
    'registry/requisitos.json': 'registro de requisitos',
    'registry/regras.json': 'registro de regras de negócio',
    'registry/decisions.json': 'registro de decisões',
    'projeto.yml': 'manifesto do projeto',
    'llms.txt': 'roteador para agentes',
    '.claude-plugin/plugin.json': 'manifesto de plugin',
}

_NUCLEO = ('registry/requisitos.json', 'registry/regras.json', 'projeto.yml')


def avaliar(raiz: Path, entradas: List[dict]) -> Dict:
    raiz = Path(raiz).resolve()
    caminhos = {e['caminho'] for e in entradas}
    achados = []

    presentes = {c: d for c, d in ARTEFATOS.items() if c in caminhos}
    usa_dk = bool(presentes)

    for caminho in presentes:
        if not caminho.endswith('.json'):
            continue
        try:
            json.loads((raiz / caminho).read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError) as exc:
            achados.append({
                'id': 'CONF-JSON',
                'titulo': f'{caminho} não é JSON válido',
                'evidencia': f'{caminho}: {exc.__class__.__name__}',
                'impacto': 'alto',
            })

    if not usa_dk:
        classificacao = 'NAO COMPATIVEL'
    elif achados:
        classificacao = 'INCONSISTENTE'
    else:
        nucleo = [c for c in _NUCLEO if c in presentes]
        if len(nucleo) == len(_NUCLEO):
            classificacao = 'COMPATIVEL'
        elif nucleo:
            classificacao = 'PARCIALMENTE COMPATIVEL'
            achados.append({
                'id': 'CONF-NUCLEO',
                'titulo': 'artefato de núcleo ausente',
                'evidencia': 'ausentes: ' + ', '.join(
                    c for c in _NUCLEO if c not in presentes),
                'impacto': 'medio',
            })
        else:
            classificacao = 'PARCIALMENTE COMPATIVEL'
            achados.append({
                'id': 'CONF-PERIFERIA',
                'titulo': 'só artefatos periféricos do DK presentes',
                'evidencia': 'presentes: ' + ', '.join(sorted(presentes)),
                'impacto': 'medio',
            })

    return {
        'usa_dk': usa_dk,
        'classificacao': classificacao,
        'artefatos': [{'caminho': c, 'papel': d}
                      for c, d in sorted(presentes.items())],
        'achados': achados,
    }
