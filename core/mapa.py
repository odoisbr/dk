#!/usr/bin/env python3
"""Mapa progressivo do repositório.

Níveis, do mais barato ao mais caro. O `dk` sobe de nível só quando a tarefa
exige — é o que impede a leitura do repositório inteiro por reflexo.

    0  sistema de arquivos: quantos arquivos, quanto pesam
    1  tipos: quanto de código, de config, de doc, de teste
    2  arquivos importantes, ranqueados, com motivo

Níveis 3 (símbolos) e 4 (relações) exigem parser e ficam para um plano futuro,
com integração opcional anunciada."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Dict

from core import classify, deteccao, scan

NIVEIS = {0: 'filesystem', 1: 'tipos', 2: 'importantes'}

_ENTRYPOINT = {
    'index.js', 'index.ts', 'main.py', '__main__.py', 'app.py', 'main.go',
    'main.java', 'index.html', 'app.js', 'server.js', 'cli.py',
}


def _importancia(entrada: dict):
    """Devolve (nível, motivo). Regra explícita, não heurística escondida."""
    caminho = entrada['caminho']
    nome = Path(caminho).name
    profundidade = len(Path(caminho).parts)

    if entrada['categoria'] == 'manifesto':
        return 'ALTA', 'manifesto do projeto'
    if entrada['categoria'] == 'documentacao-raiz':
        return 'ALTA', 'documentação de entrada do repositório'
    if nome in _ENTRYPOINT:
        return 'ALTA', 'entrypoint por convenção de nome'
    if entrada['tipo'] == 'config' and profundidade <= 2:
        return 'MEDIA', 'configuração próxima da raiz'
    if entrada['tipo'] == 'source' and profundidade <= 2:
        return 'MEDIA', 'código próximo da raiz'
    if entrada['tipo'] == 'test':
        return 'BAIXA', 'teste'
    if entrada['tipo'] == 'asset':
        return 'BAIXA', 'binário, não é lido'
    return 'BAIXA', 'sem sinal de relevância'


def montar(raiz: Path, nivel: int = 2) -> Dict:
    raiz = Path(raiz).resolve()
    entradas = [classify.classificar(e) for e in scan.varrer(raiz)]

    metricas = {
        'arquivos': len(entradas),
        'bytes': sum(e['bytes'] for e in entradas),
        'tokens_estimados_total': sum(e['tokens_estimados'] for e in entradas),
        'nota': f'estimativa — {classify.REGRA_TOKENS}',
    }

    m = {
        'nivel': nivel,
        'projeto': {},
        'estrutura': {},
        'entrypoints': [],
        'configs': [],
        'documentos': [],
        'importantes': [],
        'ignorados': scan.descartados(raiz),
        'metricas': metricas,
    }

    if nivel <= 0:
        return m

    m['projeto'] = deteccao.detectar(raiz, entradas)
    m['estrutura'] = dict(Counter(e['tipo'] for e in entradas))
    m['metricas']['linguagens'] = dict(
        Counter(e['linguagem'] for e in entradas if e['linguagem']))

    if nivel <= 1:
        return m

    for e in entradas:
        nivel_imp, motivo = _importancia(e)
        if e['categoria'] == 'manifesto' or (
                e['tipo'] == 'config' and len(Path(e['caminho']).parts) <= 2):
            m['configs'].append(e['caminho'])
        if e['tipo'] == 'doc':
            m['documentos'].append(e['caminho'])
        if Path(e['caminho']).name in _ENTRYPOINT:
            m['entrypoints'].append(e['caminho'])
        if nivel_imp in ('ALTA', 'MEDIA'):
            m['importantes'].append({
                'caminho': e['caminho'],
                'importancia': nivel_imp,
                'motivo': motivo,
                'tokens_estimados': e['tokens_estimados'],
            })

    ordem = {'ALTA': 0, 'MEDIA': 1, 'BAIXA': 2}
    m['importantes'].sort(key=lambda i: (ordem[i['importancia']], i['caminho']))
    m['metricas']['tokens_dos_importantes'] = sum(
        i['tokens_estimados'] for i in m['importantes'])
    return m
