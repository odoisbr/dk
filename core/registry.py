#!/usr/bin/env python3
"""Registros do projeto: requisitos, regras, fontes, evidências, rastreabilidade.

Dois esquemas convivem, e o real manda.

O esquema **canônico** é o que os projetos da casa já usam: `business-rules.json`,
`requirements.json`, `sources.json`, `evidence.json`, `traceability.json`. Foi
verificado num projeto vivo — 86 requisitos, 18 regras, 104 relações — e é mais
rico que o que o DK tinha: tem procedência por fonte e rastreabilidade persistida.

O esquema **do DK** — `regras.json`, `requisitos.json` — nasceu de uma fixture
escrita para o teste, não da realidade. Ele continua servindo a projeto novo que
ainda não tem registro nenhum, e some assim que o canônico existir.

`carregar` lê o que existir, na ordem de preferência, e normaliza os campos que o
núcleo consome sem descartar os originais. `gravar` devolve ao mesmo arquivo de
onde leu — o DK não cria um segundo registro ao lado do que o projeto já tem.

O `upsert` funde por id em vez de anexar: campo ausente na atualização preserva o
valor anterior, e é isso que impede o mesmo requisito voltar duplicado a cada
levantamento."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional, Tuple

from core import io

# nome lógico → arquivos aceitos, em ordem de preferência. O primeiro é o canônico.
ARQUIVOS = {
    'regras': ('business-rules.json', 'regras.json'),
    'requisitos': ('requirements.json', 'requisitos.json'),
    'fontes': ('sources.json',),
    'evidencias': ('evidence.json',),
    'rastreabilidade': ('traceability.json',),
    'historias': ('stories.json',),
    'epicos': ('epics.json',),
    'decisoes': ('decisions.json',),
    'lexico': ('lexicon.json',),
    'escopo': ('escopo.json',),
    'riscos': ('riscos.json',),
    'aceitacao': ('aceitacao.json',),
}


def _candidatos(nome: str) -> Tuple[str, ...]:
    return ARQUIVOS.get(nome, (f'{nome}.json',))


def caminho(raiz: Path, nome: str) -> Path:
    """O arquivo que existe; se nenhum existir, o último candidato — que é o do
    DK, para projeto novo. Assim o canônico é sempre preferido quando há."""
    pasta = Path(raiz) / 'registry'
    for arquivo in _candidatos(nome):
        alvo = pasta / arquivo
        if alvo.exists():
            return alvo
    return pasta / _candidatos(nome)[-1]


def esquema(raiz: Path) -> str:
    """Qual esquema o projeto usa. Aparece no relatório do audit."""
    pasta = Path(raiz) / 'registry'
    if (pasta / 'requirements.json').exists() or (pasta / 'business-rules.json').exists():
        return 'canonico'
    if (pasta / 'requisitos.json').exists() or (pasta / 'regras.json').exists():
        return 'dk'
    return 'ausente'


def _normalizar(nome: str, itens: List[dict]) -> List[dict]:
    """Acrescenta os apelidos que o núcleo consome, sem apagar os campos originais.

    Normalizar por acréscimo, e não por conversão, é o que permite `gravar`
    devolver o item ao arquivo de origem sem perder nada que o projeto tinha."""
    for item in itens:
        if not isinstance(item, dict):
            continue
        if nome == 'regras':
            item.setdefault('enunciado', item.get('title') or item.get('enunciado', ''))
            item.setdefault('citacao', item.get('description', ''))
        elif nome == 'requisitos':
            item.setdefault('titulo', item.get('title') or item.get('titulo', ''))
        if 'sources' in item and 'fonte' not in item:
            item['fonte'] = ', '.join(item['sources']) if isinstance(
                item['sources'], list) else str(item['sources'])
    return itens


def carregar(raiz: Path, nome: str) -> List[dict]:
    alvo = caminho(raiz, nome)
    if not alvo.exists():
        return []
    try:
        dados = json.loads(alvo.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return []
    if isinstance(dados, dict):
        dados = dados.get('itens') or dados.get('items') or []
    return _normalizar(nome, dados if isinstance(dados, list) else [])


def para_esquema(nome: str, item: dict, alvo: str) -> dict:
    """Dá ao item a forma do esquema de destino, antes de gravar.

    Escrever `enunciado` e `citacao` dentro de um `business-rules.json` polui o
    registro do projeto com campos que só o DK entende. O item sai daqui com os
    nomes que o esquema de destino usa, e os apelidos internos ficam de fora."""
    saida = dict(item)
    if alvo != 'canonico':
        return saida
    if nome == 'regras':
        saida.setdefault('title', saida.pop('enunciado', '') or saida.get('title', ''))
        saida.setdefault('description', saida.pop('citacao', '')
                         or saida.get('description', ''))
        saida.setdefault('status', 'proposta')
    elif nome == 'requisitos':
        saida.setdefault('title', saida.pop('titulo', '') or saida.get('title', ''))
        saida.setdefault('type', 'funcional')
        saida.setdefault('status', 'proposta')
    for interno in ('enunciado', 'citacao', 'titulo', 'fonte'):
        saida.pop(interno, None)
    return saida


def gravar(raiz: Path, nome: str, itens: List[dict]) -> None:
    alvo = esquema(raiz)
    io.atomic_json(caminho(raiz, nome),
                   [para_esquema(nome, i, alvo) for i in itens])


def upsert(itens: List[dict], novo: dict, chave: str = 'id') -> Tuple[List[dict], str]:
    """Funde `novo` na lista. Campo ausente em `novo` preserva o valor anterior."""
    saida = [dict(i) for i in itens]
    for i, existente in enumerate(saida):
        if existente.get(chave) == novo.get(chave):
            fundido = dict(existente)
            fundido.update(novo)
            saida[i] = fundido
            return saida, 'atualizado'
    saida.append(dict(novo))
    return saida, 'criado'


def relacoes(raiz: Path, relacao: Optional[str] = None) -> List[dict]:
    """As arestas de `traceability.json`, opcionalmente filtradas por tipo."""
    todas = carregar(raiz, 'rastreabilidade')
    if relacao is None:
        return todas
    return [t for t in todas if t.get('relation') == relacao]
