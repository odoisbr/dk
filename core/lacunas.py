#!/usr/bin/env python3
"""Lacunas: o que o checklist prevê e o registro não tem.

A regra que o community fixou e aqui vira código: lacuna só existe com âncora no
checklist. "Seria bom saber" não entra. Por isso o checklist é dado versionado —
mudar o que se cobra é editar JSON, não Python.

O status é conservador: PARCIAL quando há sinal isolado, AUSENTE quando não há
nenhum. COBERTO exige sinal em mais de um registro, porque uma menção solta não
é entendimento."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from core import registry

CHECKLIST = (Path(__file__).resolve().parents[1] / 'templates'
             / 'checklist-discovery.json')


def carregar_checklist() -> List[dict]:
    return json.loads(CHECKLIST.read_text(encoding='utf-8'))['itens']


def _corpus(raiz: Path) -> List[str]:
    partes = []
    for nome in ('regras', 'requisitos'):
        for item in registry.carregar(raiz, nome):
            partes.append(' '.join(str(v) for v in item.values()))
    return partes


def analisar(raiz: Path) -> List[Dict]:
    raiz = Path(raiz)
    partes = _corpus(raiz)
    texto = ' '.join(partes).lower()

    achados = []
    for i, item in enumerate(carregar_checklist(), start=1):
        ocorrencias = [s for s in item['sinais'] if s.lower() in texto]
        registros_com_sinal = sum(
            1 for p in partes
            if any(s.lower() in p.lower() for s in item['sinais']))

        if not ocorrencias:
            status = 'AUSENTE'
            evidencia = ('nenhum registro menciona: '
                         + ', '.join(item['sinais'][:4]))
        elif registros_com_sinal >= 2:
            status = 'COBERTO'
            evidencia = (f'{registros_com_sinal} registros mencionam '
                         + ', '.join(sorted(set(ocorrencias))[:3]))
        else:
            status = 'PARCIAL'
            evidencia = ('menção isolada a '
                         + ', '.join(sorted(set(ocorrencias))[:3])
                         + ' — uma menção não é entendimento')

        achados.append({
            'id': f'L-{i:02d}',
            'item': item['id'],
            'tema': item['tema'],
            'pergunta': item['pergunta'],
            'status': status,
            'prioridade': item['prioridade'],
            'evidencia': evidencia,
        })
    return achados
