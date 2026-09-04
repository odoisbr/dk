#!/usr/bin/env python3
"""Cobertura: o que existe de um lado e não tem par do outro.

O que se cruza depende do esquema que o projeto usa, e o real não é o que o DK
supunha.

No esquema **canônico**, requisito e regra são irmãos: os dois se ancoram em
`sources`, e o requisito se liga à história por `traceability`. Não existe
"requisito deriva de regra" — isso era invenção do DK. Então o que se cobra é
procedência e planejamento:

    requisito sem fonte      ninguém sabe de onde veio
    regra sem fonte          idem
    fonte apontando para arquivo que sumiu   procedência quebrada
    requisito sem história   levantado e não planejado

No esquema **do DK**, usado por projeto que ainda não tem registro, vale o
vínculo simples `deriva_de`.

Em qualquer esquema: requisito que não aparece em entregável é trabalho que o
cliente não vai ver."""
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
    esquema = registry.esquema(raiz)
    regras = registry.carregar(raiz, 'regras')
    requisitos = registry.carregar(raiz, 'requisitos')

    texto = _texto_dos_entregaveis(raiz)
    sem_entregavel = [q['id'] for q in requisitos if q['id'] not in texto]

    base = {
        'esquema': esquema,
        'requisitos_sem_entregavel': sem_entregavel,
        'totais': {'regras': len(regras), 'requisitos': len(requisitos)},
    }

    if esquema == 'canonico':
        fontes = {f['id'] for f in registry.carregar(raiz, 'fontes')}
        ligados = {t['from'] for t in registry.relacoes(raiz, 'pertence_a_historia')}

        sem_fonte_req = [q['id'] for q in requisitos if not q.get('sources')]
        sem_fonte_regra = [r['id'] for r in regras if not r.get('sources')]
        fonte_quebrada = sorted({
            f"{item['id']}→{s}"
            for item in list(requisitos) + list(regras)
            for s in (item.get('sources') or [])
            if s not in fontes})
        sem_historia = [q['id'] for q in requisitos if q['id'] not in ligados]

        base.update({
            'requisitos_sem_fonte': sem_fonte_req,
            'regras_sem_fonte': sem_fonte_regra,
            'fonte_inexistente': fonte_quebrada,
            'requisitos_sem_historia': sem_historia,
            # No canônico não há vínculo requisito→regra; não invente um.
            'regras_sem_requisito': [],
            'requisitos_sem_regra': [],
        })
        base['totais']['fontes'] = len(fontes)
        base['totais']['relacoes'] = len(registry.carregar(raiz, 'rastreabilidade'))
        return base

    ids_regras = {r['id'] for r in regras}
    base.update({
        'regras_sem_requisito': regras_sem_requisito(requisitos, regras),
        'requisitos_sem_regra': [q['id'] for q in requisitos
                                 if q.get('deriva_de') not in ids_regras],
        'requisitos_sem_fonte': [],
        'regras_sem_fonte': [],
        'fonte_inexistente': [],
        'requisitos_sem_historia': [],
    })
    return base
