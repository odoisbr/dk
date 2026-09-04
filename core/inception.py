#!/usr/bin/env python3
"""Lean Inception: a agenda das onze atividades cobrada contra o registro.

O formato não foi inventado. `registry/lean-inception.json` existe em projeto
vivo com `tipo`, `ordem`, `titulo`, `status`, `conteudo` e `sources`, e é essa a
forma que este módulo lê. O registro do projeto manda; a agenda diz o que falta.

A agenda é dado — `templates/agenda-inception.json` —, não código: mudar o que se
cobra é editar JSON. Cada atividade declara os campos que a tornam válida, e é aí
que mora a diferença entre atividade *registrada* e atividade *coberta*: o Canvas
MVP com dois dos seis campos existe no arquivo e não fecha compromisso nenhum.

O que este módulo conclui é estrutura: presença, campo obrigatório e âncora em
fonte. Se a onda 1 fecha uma jornada, se a persona é real, se o objetivo é
mensurável — isso é leitura, e sai com `decidido_por: skill`."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from core import registry

AGENDA = (Path(__file__).resolve().parents[1] / 'templates'
          / 'agenda-inception.json')


def agenda() -> dict:
    return json.loads(AGENDA.read_text(encoding='utf-8'))


def _achado(ident, titulo, evidencia, impacto='medio', decidido='codigo') -> Dict:
    return {'id': ident, 'titulo': titulo, 'evidencia': evidencia,
            'impacto': impacto, 'decidido_por': decidido}


def _preenchido(item: dict, campo: str) -> bool:
    valor = item.get(campo)
    if isinstance(valor, str):
        return bool(valor.strip())
    return bool(valor)


def avaliar(raiz: Path) -> Dict:
    """Estado da inception: o que está coberto, o que falta e o que está torto."""
    raiz = Path(raiz)
    dados = agenda()
    itens = registry.carregar(raiz, 'inception')
    achados: List[Dict] = []

    if not itens:
        # Verdade vácua tem classe própria no DK: zero contra zero não passa.
        achados.append(_achado(
            'INC-SEM-REGISTRO', 'nenhuma atividade de inception registrada',
            'registry/lean-inception.json ausente ou vazio — a inception não '
            'está incompleta, está por começar', impacto='alto'))
        return {'estado': 'por-comecar', 'atividades': [], 'cobertas': 0,
                'total': len(dados['atividades']), 'percentual': 0,
                'achados': achados}

    por_tipo: Dict[str, List[dict]] = {}
    for item in itens:
        por_tipo.setdefault(str(item.get('tipo', '')), []).append(item)

    conhecidos = {a['tipo'] for a in dados['atividades']}
    conhecidos |= {c['tipo'] for c in dados['complementos']}
    for tipo, grupo in sorted(por_tipo.items()):
        if tipo not in conhecidos:
            achados.append(_achado(
                'INC-FORA-DA-AGENDA', 'tipo fora da agenda da inception',
                f'{len(grupo)} item(ns) do tipo {tipo!r} — a agenda tem '
                + ', '.join(sorted(conhecidos))))

    for item in itens:
        if not item.get('sources'):
            achados.append(_achado(
                'INC-SEM-FONTE', 'atividade sem âncora em fonte',
                f"{item.get('id', '?')} ({item.get('tipo', '?')}) não cita "
                'nenhuma fonte — sem procedência, é opinião registrada'))

    atividades = []
    for a in dados['atividades'] + dados['complementos']:
        grupo = por_tipo.get(a['tipo'], [])
        faltando = sorted({c for item in grupo for c in a['exige']
                           if not _preenchido(item, c)})
        if not grupo:
            estado = 'ausente'
            evidencia = f"nada registrado — {a['pergunta']}"
        elif faltando:
            estado = 'incompleta'
            evidencia = (f'{len(grupo)} item(ns), faltando: '
                         + ', '.join(faltando))
            achados.append(_achado(
                'INC-CAMPO', f"{a['nome']} sem campo obrigatório",
                'faltando ' + ', '.join(faltando)
                + f" em {', '.join(i.get('id', '?') for i in grupo)}"))
        else:
            estado = 'coberta'
            evidencia = f'{len(grupo)} item(ns) registrados'
        atividades.append({'n': a.get('n'), 'tipo': a['tipo'],
                           'nome': a['nome'], 'estado': estado,
                           'evidencia': evidencia})

    numeradas = [x for x in atividades if x['n']]
    cobertas = [x for x in numeradas if x['estado'] == 'coberta']
    total = len(numeradas)
    return {
        'estado': 'em-andamento' if len(cobertas) < total else 'completa',
        'atividades': atividades,
        'cobertas': len(cobertas),
        'total': total,
        'percentual': round(100 * len(cobertas) / total) if total else 0,
        'achados': achados,
    }
