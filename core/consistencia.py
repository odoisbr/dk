#!/usr/bin/env python3
"""Os seis tipos de inconsistência entre requisitos, portados do community.

A divisão de trabalho é explícita em cada achado, no campo `decidido_por`:

    codigo  a verificação é determinística e o achado é conclusão
    skill   o código marca o candidato e a decisão exige leitura

Fingir determinismo onde não há é pior que não ter a checagem: produz achado
falso com cara de fato."""
from __future__ import annotations
import re
import unicodedata
from typing import Dict, List

TIPOS = {
    'CONFLITO': 'dois requisitos que não podem ser verdadeiros ao mesmo tempo',
    'DUPLICATA': 'mesma necessidade expressa de formas diferentes',
    'ORFAO': 'requisito sem âncora rastreável',
    'REFERENCIA-INDEFINIDA': 'menciona entidade não definida em lugar nenhum',
    'NF-SEM-CRITERIO': 'requisito não-funcional sem critério mensurável',
    'REGRA-CIRCULAR': 'regra A depende de B, que depende de A',
}

_VAGOS = ('rápido', 'rapido', 'rápida', 'rapida', 'intuitiv', 'amigável',
          'amigavel', 'fácil', 'facil', 'simples de usar', 'performático',
          'performatico', 'escalável', 'escalavel', 'robusto', 'moderno')

_MENSURAVEL = re.compile(
    r'\d+\s*(s\b|seg|segundo|ms|milissegundo|min|minuto|h\b|hora|%|kb|mb|gb|'
    r'usuário|usuario|requisi|transaç|transac)', re.I)

_PARADA = set('de da do das dos e o a os as um uma para com por em no na nos '
              'nas que se ao aos deve poder pode ser estar'.split())


def _normaliza(token: str) -> str:
    """Dobra acento e plural antes de comparar.

    Duplicata real aparece assim: "revogar o convênio" e "revogar convênios".
    Sem esta normalização a comparação erra justamente o caso que ela existe
    para pegar. A dobra não precisa ser linguisticamente correta — precisa ser
    a mesma dos dois lados."""
    dobrado = unicodedata.normalize('NFKD', token)
    dobrado = ''.join(c for c in dobrado if not unicodedata.combining(c))
    if len(dobrado) > 4 and dobrado.endswith('s'):
        dobrado = dobrado[:-1]
    return dobrado


def _tokens(texto: str) -> set:
    return {_normaliza(t) for t in re.findall(r'[a-zà-ú]{3,}', texto.lower())
            if t not in _PARADA}


def _similaridade(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _achado(tipo: str, itens: List[str], evidencia: str, urgencia: str,
            decidido_por: str) -> Dict:
    return {
        'tipo': tipo,
        'descricao': TIPOS[tipo],
        'itens': itens,
        'evidencia': evidencia,
        'urgencia': urgencia,
        'decidido_por': decidido_por,
    }


def analisar(regras: List[dict], requisitos: List[dict]) -> List[Dict]:
    achados = []
    ids_regras = {r['id'] for r in regras}

    # Tipo 3 — ÓRFÃO
    for q in requisitos:
        origem = q.get('deriva_de')
        if not origem or origem not in ids_regras:
            achados.append(_achado(
                'ORFAO', [q['id']],
                f"{q['id']} aponta para {origem!r}, que não existe em regras",
                'RESOLVE-ANTES-DO-DESIGN', 'codigo'))

    # Tipo 2 — DUPLICATA
    for i in range(len(requisitos)):
        for j in range(i + 1, len(requisitos)):
            a, b = requisitos[i], requisitos[j]
            s = _similaridade(a.get('titulo', ''), b.get('titulo', ''))
            if s >= 0.6:
                achados.append(_achado(
                    'DUPLICATA', [a['id'], b['id']],
                    f"similaridade {s:.0%} entre {a['id']} e {b['id']}: "
                    f"{a.get('titulo', '')[:40]!r} × {b.get('titulo', '')[:40]!r}",
                    'RESOLVE-ANTES-DO-DESIGN', 'codigo'))

    # Tipo 5 — NF-SEM-CRITÉRIO
    for q in requisitos:
        titulo = q.get('titulo', '')
        baixo = titulo.lower()
        vagos = [v for v in _VAGOS if v in baixo]
        if vagos and not _MENSURAVEL.search(titulo):
            achados.append(_achado(
                'NF-SEM-CRITERIO', [q['id']],
                f"{q['id']} usa {', '.join(sorted(set(vagos)))} sem número "
                f"nem unidade: {titulo[:60]!r}",
                'RESOLVE-ANTES-DO-DESIGN', 'codigo'))

    # Tipo 6 — REGRA-CIRCULAR
    grafo = {r['id']: list(r.get('depende') or []) for r in regras}
    achados += _ciclos(grafo)

    # Tipo 4 — REFERÊNCIA-INDEFINIDA (parcial: o código acha, a skill julga)
    definidos = ' '.join(
        [r.get('enunciado', '') for r in regras]
        + [q.get('titulo', '') for q in requisitos])
    for q in requisitos:
        for nome in re.findall(r'\b(?:Portal|Sistema|Módulo|Modulo|API)\s+'
                               r'([A-ZÀ-Ú][\wÀ-ú]+)', q.get('titulo', '')):
            if definidos.count(nome) <= 1:
                achados.append(_achado(
                    'REFERENCIA-INDEFINIDA', [q['id']],
                    f"{q['id']} menciona {nome!r}, que aparece uma vez só em "
                    'todo o registro — pode ser integração não especificada',
                    'PODE-POSTERGAR', 'skill'))

    # Tipo 1 — CONFLITO: candidato, nunca conclusão
    for i in range(len(requisitos)):
        for j in range(i + 1, len(requisitos)):
            a, b = requisitos[i], requisitos[j]
            s = _similaridade(a.get('titulo', ''), b.get('titulo', ''))
            if 0.3 <= s < 0.6 and a.get('deriva_de') != b.get('deriva_de'):
                achados.append(_achado(
                    'CONFLITO', [a['id'], b['id']],
                    f"{a['id']} e {b['id']} falam do mesmo assunto ({s:.0%}) "
                    'e vêm de regras diferentes — o código não decide se há '
                    'conflito; a skill lê e julga',
                    'PODE-POSTERGAR', 'skill'))

    return achados


def _ciclos(grafo: Dict[str, List[str]]) -> List[Dict]:
    """Busca em profundidade com pilha explícita: sem recursão, sem estouro."""
    achados = []
    relatados = set()
    for inicio in sorted(grafo):
        pilha = [(inicio, [inicio])]
        while pilha:
            no, caminho = pilha.pop()
            for prox in grafo.get(no, []):
                if prox in caminho:
                    ciclo = caminho[caminho.index(prox):]
                    chave = tuple(sorted(set(ciclo)))
                    if chave in relatados:
                        continue
                    relatados.add(chave)
                    achados.append(_achado(
                        'REGRA-CIRCULAR', sorted(set(ciclo)),
                        'ciclo de dependência: ' + ' → '.join(ciclo + [prox]),
                        'BLOQUEIA-AVANCO', 'codigo'))
                elif prox in grafo:
                    pilha.append((prox, caminho + [prox]))
    return achados
