#!/usr/bin/env python3
"""Contrato de cada entregável, cobrado por código.

A skill de ata do community enunciava estas regras em prosa — "sem coluna de
status", "decisão não é pendência", "a ata só fecha sem marcadores". Prosa que
ninguém verifica é intenção. Aqui elas reprovam."""
from __future__ import annotations
import re
from typing import Dict, List

CONTRATOS: Dict[str, dict] = {
    'ata': {
        'titulo': 'Ata de Reunião',
        'secoes': [
            'Identificação',
            'Participantes',
            'Resumo Executivo',
            'Tópicos Discutidos',
            'Principais Decisões',
            'Encaminhamentos e Ações',
            'Pontos em Aberto / Pendências',
        ],
        'proibidas': ['Próximos Passos', 'Observações Complementares'],
    },
    'handoff': {
        'titulo': 'Handoff para Desenvolvimento',
        'secoes': [
            'Visão geral',
            'Escopo deste handoff',
            'Design tokens',
            'Inventário de componentes',
            'Especificação por tela',
            'Fluxos críticos',
            'Rastreabilidade',
            'Pendências e dependências',
        ],
        'proibidas': [],
    },
    'requisitos': {
        'titulo': 'Documento de Requisitos de Design',
        'secoes': [
            'Contexto e objetivo',
            'Estrutura funcional',
            'Critérios de sucesso',
            'Priorização',
            'Dependências e premissas',
            'Validação e Aprovação',
        ],
        'proibidas': [],
    },
}

_MARCADORES = ('[verificar]', '[A CONFIRMAR]')


def _tem_secao(corpo: str, nome: str) -> bool:
    alvo = nome.lower()
    for linha in corpo.splitlines():
        if linha.startswith('#') and alvo in linha.lower():
            return True
    return False


def validar(tipo: str, corpo_md: str) -> List[dict]:
    contrato = CONTRATOS.get(tipo)
    if not contrato:
        return [{'id': 'TIPO-DESCONHECIDO',
                 'titulo': f'não há contrato para {tipo!r}',
                 'evidencia': f'tipos conhecidos: {", ".join(sorted(CONTRATOS))}',
                 'impacto': 'alto'}]

    prefixo = tipo[:3].upper()
    achados = []

    for nome in contrato['secoes']:
        if not _tem_secao(corpo_md, nome):
            achados.append({
                'id': f'{prefixo}-SECAO',
                'titulo': f'seção obrigatória ausente: {nome}',
                'evidencia': f'nenhum cabeçalho contém "{nome}"',
                'impacto': 'alto',
            })

    for nome in contrato['proibidas']:
        if _tem_secao(corpo_md, nome):
            achados.append({
                'id': f'{prefixo}-PROIBIDA',
                'titulo': f'seção que não entra por padrão: {nome}',
                'evidencia': f'cabeçalho "{nome}" presente',
                'impacto': 'medio',
            })

    for marcador in _MARCADORES:
        if marcador in corpo_md:
            achados.append({
                'id': f'{prefixo}-MARCADOR',
                'titulo': f'marcador pendente no documento: {marcador}',
                'evidencia': f'{corpo_md.count(marcador)} ocorrência(s) de '
                             f'{marcador} — o documento só fecha sem marcador',
                'impacto': 'alto',
            })

    if tipo == 'ata':
        for linha in corpo_md.splitlines():
            if not linha.strip().startswith('|'):
                continue
            celulas = [c.strip().lower()
                       for c in linha.strip().strip('|').split('|')]
            if 'ação' in celulas and 'status' in celulas:
                achados.append({
                    'id': 'ATA-STATUS',
                    'titulo': 'encaminhamentos com coluna de status',
                    'evidencia': f'linha: {linha.strip()[:70]} — a ata é registro '
                                 'final; a tabela é Ação · Responsável · Prazo',
                    'impacto': 'medio',
                })
                break

    if tipo == 'requisitos' and not re.search(r'^#+.*\bE-\d', corpo_md, re.M):
        achados.append({
            'id': 'REQ-EPICO',
            'titulo': 'nenhum épico identificado',
            'evidencia': 'não há cabeçalho no padrão "Épico E-01"',
            'impacto': 'alto',
        })

    return achados
