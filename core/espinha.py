#!/usr/bin/env python3
"""Parte determinística da espinha: estrutura, identifica e reconcilia.

O que exige raciocínio — redigir a regra em linguagem de negócio, julgar se duas
regras são a mesma — fica com a skill. O que é forma, extração e vínculo fica aqui,
onde é testável e barato.

LIMITAÇÃO CONHECIDA da identidade: o id da regra é posicional (ordem da fala na
ata). É isso que faz o texto revisado de uma fala ATUALIZAR a regra existente em
vez de criar outra ao lado — o comportamento que o teste de ciclo cobra. O custo
é que inserir uma fala no meio desloca os ids seguintes. A identidade estável por
âncora de fala é trabalho do plano da etapa `entender`; até lá, ata revisada deve
preservar a ordem das falas."""
from __future__ import annotations
import re
from typing import Dict, List

_DATA = re.compile(r'\b(\d{2})/(\d{2})(?:/(\d{2,4}))?\b')
_FALA = re.compile(r'^([A-ZÀ-Ú][\wÀ-ú.\- ]{1,40}?)\s*(?:\(([^)]*)\))?\s*:\s*(.+)$')


def ata(texto_bruto: str) -> Dict:
    """Estrutura o insumo bruto: data, participantes e falas atribuídas."""
    linhas = [l.strip() for l in texto_bruto.splitlines() if l.strip()]
    data = ''
    m = _DATA.search(texto_bruto)
    if m:
        data = '/'.join(p for p in m.groups() if p)

    falas = []
    participantes = []
    for linha in linhas:
        f = _FALA.match(linha)
        if not f:
            continue
        nome = f.group(1).strip()
        if nome not in participantes:
            participantes.append(nome)
        falas.append({'quem': nome, 'papel': (f.group(2) or '').strip(),
                      'fala': f.group(3).strip()})

    titulo = linhas[0] if linhas else ''
    return {'titulo': titulo, 'data': data,
            'participantes': participantes, 'falas': falas}


_MARCA_REGRA = re.compile(
    r'\b(não|nao|sempre|nunca|só|so|apenas|quem|quando|deve|precisa|fica|continua)\b',
    re.I)


def regras(ata_estruturada: Dict) -> List[Dict]:
    """Candidatas a regra de negócio, cada uma com a citação que a originou.

    Candidata, não regra: quem decide se vira regra é gente. O que o código
    garante é que nenhuma nasce sem procedência."""
    saida = []
    for fala in ata_estruturada.get('falas', []):
        if not _MARCA_REGRA.search(fala['fala']):
            continue
        saida.append({
            'id': f'RN-{len(saida) + 1:03d}',
            'enunciado': fala['fala'],
            'citacao': fala['fala'],
            'fonte': f"{ata_estruturada.get('titulo', '')} — {fala['quem']}",
            'autoridade': 'cliente' if 'gestor' in fala.get('papel', '').lower()
                          else 'equipe',
        })
    return saida


def requisitos(lista_regras: List[Dict]) -> List[Dict]:
    """Um requisito por regra, vinculado à regra que o originou."""
    return [{
        'id': f'REQ-{i:03d}',
        'titulo': r['enunciado'],
        'deriva_de': r['id'],
        'fonte': r.get('fonte', ''),
    } for i, r in enumerate(lista_regras, start=1)]


def cobertura(lista_requisitos: List[Dict], lista_regras: List[Dict]) -> Dict:
    """Toda regra precisa de pelo menos um requisito. O que faltar é furo."""
    cobertas = {q.get('deriva_de') for q in lista_requisitos}
    faltando = [r['id'] for r in lista_regras if r['id'] not in cobertas]
    return {
        'total_regras': len(lista_regras),
        'total_requisitos': len(lista_requisitos),
        'regras_sem_requisito': faltando,
    }
