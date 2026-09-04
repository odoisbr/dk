#!/usr/bin/env python3
"""Cobertura: o que existe de um lado e não tem par do outro.

Três cruzamentos. Regra sem requisito é escopo que ninguém vai construir.
Requisito sem regra é escopo que ninguém pediu. Requisito sem entregável é
trabalho que o cliente não vai ver."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

from core import padrao, registry


def regras_sem_requisito(lista_requisitos: List[dict],
                         lista_regras: List[dict]) -> List[str]:
    cobertas = {q.get('deriva_de') for q in lista_requisitos}
    return [r['id'] for r in lista_regras if r['id'] not in cobertas]


def _texto_dos_entregaveis(raiz: Path) -> str:
    partes = []
    for chave in ('requisitos', 'visao', 'ata'):
        pasta = raiz / padrao.destino(chave)
        if not pasta.is_dir():
            continue
        for arq in sorted(pasta.iterdir()):
            if arq.suffix.lower() in ('.html', '.md'):
                partes.append(arq.read_text(encoding='utf-8', errors='replace'))
    return '\n'.join(partes)


def matriz(raiz: Path) -> Dict:
    raiz = Path(raiz)
    regras = registry.carregar(raiz, 'regras')
    requisitos = registry.carregar(raiz, 'requisitos')
    ids_regras = {r['id'] for r in regras}

    sem_regra = [q['id'] for q in requisitos
                 if q.get('deriva_de') not in ids_regras]

    texto = _texto_dos_entregaveis(raiz)
    sem_entregavel = [q['id'] for q in requisitos if q['id'] not in texto]

    return {
        'regras_sem_requisito': regras_sem_requisito(requisitos, regras),
        'requisitos_sem_regra': sem_regra,
        'requisitos_sem_entregavel': sem_entregavel,
        'totais': {
            'regras': len(regras),
            'requisitos': len(requisitos),
        },
    }
