#!/usr/bin/env python3
"""Parte determinística da espinha: estrutura, identifica e reconcilia.

O que exige raciocínio — redigir a regra em linguagem de negócio, julgar se duas
regras são a mesma — fica com a skill. O que é forma, extração e vínculo fica aqui,
onde é testável e barato.

IDENTIDADE: cada candidata sai com `origem_chave` — arquivo de insumo mais
posição da fala — e sem id. Quem atribui o id é a etapa de gravação, que consulta o contador do
projeto: `RN-001` gerado do zero colidia com a `RN-001` que o projeto real já
tinha. A `origem_chave` é o que faz a revisão da mesma ata atualizar em vez de
duplicar.

Revisar é editar o mesmo insumo. Insumo novo é reunião nova, e gera candidatas
novas — que é o comportamento correto.

O custo remanescente: inserir uma fala no meio do insumo desloca a posição das
seguintes, e elas viram candidatas novas. Insumo revisado deve preservar a ordem
das falas."""
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


def regras(ata_estruturada: Dict, origem: str = '') -> List[Dict]:
    """Candidatas a regra de negócio, cada uma com a citação que a originou.

    Candidata, não regra: quem decide se vira regra é gente. O que o código
    garante é que nenhuma nasce sem procedência."""
    saida = []
    for fala in ata_estruturada.get('falas', []):
        if not _MARCA_REGRA.search(fala['fala']):
            continue
        saida.append({
            # Chave de origem: o arquivo de insumo mais a posição da fala.
            #
            # O insumo, e não o título da ata: revisar uma transcrição é editar
            # o mesmo arquivo, e chavear pelo título fazia "Reunião 14/08" e
            # "Reunião 28/08" virarem origens diferentes — a revisão duplicava
            # em vez de atualizar, que é exatamente o furo a impedir.
            #
            # O id definitivo vem do contador do projeto: posicional colide com
            # o que o projeto já tem.
            'origem_chave': f"{origem or ata_estruturada.get('titulo', '')}"
                            f"#{len(saida) + 1}",
            'id': '',
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
        'origem_chave': r.get('origem_chave', ''),
        'id': '',
        'titulo': r['enunciado'],
        'deriva_de': r['id'],
        'fonte': r.get('fonte', ''),
    } for r in lista_regras]


def cobertura(lista_requisitos: List[Dict], lista_regras: List[Dict]) -> Dict:
    """Toda regra precisa de pelo menos um requisito. O que faltar é furo.

    A conta vive em `core.cobertura`; aqui é só a porta que a espinha usa. Duas
    implementações da mesma conta divergem — foi o que a auditoria mediu no Kit."""
    from core import cobertura as _cobertura
    faltando = _cobertura.regras_sem_requisito(lista_requisitos, lista_regras)
    return {
        'total_regras': len(lista_regras),
        'total_requisitos': len(lista_requisitos),
        'regras_sem_requisito': faltando,
    }
