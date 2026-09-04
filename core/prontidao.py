#!/usr/bin/env python3
"""O gate do handoff: o pipeline inteiro cobrado de uma vez.

Nenhuma verificação nova nasce aqui. O handoff é o lugar onde as verificações que
cada etapa já faz são cobradas juntas — e é isso que dá sentido a ele ser a última
etapa.

Todo bloqueio diz qual etapa resolve e qual comando rodar. Bloqueio sem saída é só
um muro."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

from core import (cobertura, consistencia, lacunas, padrao, prototipo, registry)


def _item(nome, estado, evidencia, resolve_em, comando) -> Dict:
    return {'nome': nome, 'estado': estado, 'evidencia': evidencia,
            'resolve_em': resolve_em, 'comando': comando}


def _fechar(itens: List[Dict], raiz: Path) -> Dict:
    """Acrescenta os itens que não dependem do registro e fecha o resultado."""
    ja = {i['nome'] for i in itens}

    if 'lacunas' not in ja:
        lac = lacunas.analisar(raiz)
        criticas = [a for a in lac
                    if a['prioridade'] == 'CRITICA' and a['status'] == 'AUSENTE']
        parciais = [a for a in lac if a['status'] == 'PARCIAL']
        if criticas:
            itens.append(_item(
                'lacunas', 'bloqueio',
                f'{len(criticas)} lacuna(s) crítica(s) ausente(s): '
                + ', '.join(a['tema'] for a in criticas),
                'levantar', 'dk levantar --projeto <raiz> --insumo <arquivo>'))
        elif parciais:
            itens.append(_item(
                'lacunas', 'aviso',
                f'{len(parciais)} item(ns) do checklist só com menção isolada',
                'levantar', 'dk levantar --projeto <raiz> --insumo <arquivo>'))
        else:
            itens.append(_item('lacunas', 'ok', 'checklist de discovery coberto',
                               'levantar', 'dk levantar --projeto <raiz>'))

    if 'padrao' not in ja:
        estrutura = padrao.verificar(raiz)
        altos = [a for a in estrutura if a['impacto'] == 'alto']
        if altos:
            itens.append(_item(
                'padrao', 'bloqueio',
                f'{len(altos)} violação(ões) estrutural(is): '
                + '; '.join(a['evidencia'][:60] for a in altos[:3]),
                'audit', 'dk audit --projeto <raiz>'))
        elif estrutura:
            itens.append(_item(
                'padrao', 'aviso',
                f'{len(estrutura)} achado(s) estrutural(is) de impacto menor',
                'audit', 'dk audit --projeto <raiz>'))
        else:
            itens.append(_item('padrao', 'ok',
                               'estrutura do projeto em conformidade',
                               'audit', 'dk audit --projeto <raiz>'))

    if 'prototipo' not in ja:
        proto = prototipo.verificar(raiz)
        proto_altos = [a for a in proto if a['impacto'] == 'alto']
        if proto_altos:
            itens.append(_item(
                'prototipo', 'bloqueio',
                f'{len(proto_altos)} violação(ões) de padrão no protótipo: '
                + '; '.join(f"regra {a['regra']}" for a in proto_altos[:4]),
                'prototipar', 'dk prototipar --projeto <raiz> --verificar'))
        elif proto:
            itens.append(_item(
                'prototipo', 'aviso',
                f'{len(proto)} achado(s) de padrão no protótipo',
                'prototipar', 'dk prototipar --projeto <raiz> --verificar'))
        else:
            itens.append(_item('prototipo', 'ok', 'protótipo dentro do padrão',
                               'prototipar',
                               'dk prototipar --projeto <raiz> --verificar'))

    bloqueios = [i for i in itens if i['estado'] == 'bloqueio']
    avisos = [i for i in itens if i['estado'] == 'aviso']
    return {'pronto': not bloqueios, 'bloqueios': bloqueios,
            'avisos': avisos, 'itens': itens}


def avaliar(raiz: Path) -> Dict:
    raiz = Path(raiz)
    itens = []

    cob = cobertura.matriz(raiz)
    orfas = cob['regras_sem_requisito']
    sem_regra = cob['requisitos_sem_regra']

    # Verdade vacuosa: com zero regras e zero requisitos, "toda regra tem
    # requisito", "todo requisito está no entregável" e "nenhuma inconsistência"
    # são todas verdadeiras — e todas enganosas. Um projeto vazio passaria em três
    # dos seis itens do gate, que é justamente o caso pior.
    #
    # Corrigir item a item não bastou: é uma classe de defeito, e vale para todo
    # item que depende do registro. Vazio bloqueia os três de uma vez, com o mesmo
    # motivo, e o gate diz que está vazio em vez de dizer que está fechado.
    if not cob['totais']['regras'] and not cob['totais']['requisitos']:
        motivo = ('nenhuma regra e nenhum requisito registrados — projeto vazio '
                  'não está pronto, está por começar')
        for nome in ('cobertura', 'entregaveis', 'consistencia'):
            itens.append(_item(nome, 'bloqueio', motivo, 'levantar',
                               'dk levantar --projeto <raiz> --insumo <arquivo>'))
        return _fechar(itens, raiz)

    if orfas or sem_regra:
        partes = []
        if orfas:
            partes.append('regra sem requisito: ' + ', '.join(orfas))
        if sem_regra:
            partes.append('requisito sem regra: ' + ', '.join(sem_regra))
        itens.append(_item('cobertura', 'bloqueio', ' · '.join(partes),
                           'entender', 'dk entender --projeto <raiz>'))
    else:
        itens.append(_item(
            'cobertura', 'ok',
            f"{cob['totais']['regras']} regras e {cob['totais']['requisitos']} "
            'requisitos, todos com par', 'entender',
            'dk entender --projeto <raiz>'))

    fora = cob['requisitos_sem_entregavel']
    if fora:
        itens.append(_item(
            'entregaveis', 'bloqueio',
            'requisito que não aparece em nenhum entregável: ' + ', '.join(fora),
            'entregar', 'dk entregar --tipo requisitos --projeto <raiz>'))
    else:
        itens.append(_item('entregaveis', 'ok',
                           'todo requisito aparece em algum entregável',
                           'entregar', 'dk entregar --projeto <raiz>'))

    inc = consistencia.analisar(registry.carregar(raiz, 'regras'),
                                registry.carregar(raiz, 'requisitos'))
    bloqueia = [a for a in inc if a['urgencia'] == 'BLOQUEIA-AVANCO']
    candidatos = [a for a in inc if a['decidido_por'] == 'skill']
    if bloqueia:
        itens.append(_item(
            'consistencia', 'bloqueio',
            f'{len(bloqueia)} inconsistência(s) que bloqueiam avanço: '
            + ', '.join(sorted({a['tipo'] for a in bloqueia})),
            'entender', 'dk entender --projeto <raiz>'))
    elif candidatos:
        itens.append(_item(
            'consistencia', 'aviso',
            f'{len(candidatos)} candidato(s) que a skill precisa julgar antes '
            'de fechar', 'entender', 'dk entender --projeto <raiz>'))
    else:
        itens.append(_item('consistencia', 'ok',
                           f'{len(inc)} achado(s), nenhum bloqueante',
                           'entender', 'dk entender --projeto <raiz>'))


    return _fechar(itens, raiz)
