#!/usr/bin/env python3
"""Leitor do subconjunto de YAML que a especificação de componente usa.

Não é um parser de YAML. É um leitor do que o contrato precisa: mapa aninhado,
lista de escalares, lista de mapas, escalar com aspas ou sem, comentário e linha
em branco. Âncora, alias, bloco literal, fluxo `{a: 1}` e multi-documento **não**
são suportados — e, em vez de adivinhar, `carregar` levanta erro dizendo a linha.

O que esta função não entende, ela não finge entender. Adivinhar estrutura de
especificação é pior que recusar: produz componente "válido" que não é."""
from __future__ import annotations
import re
from typing import Any, List, Tuple

_NAO_SUPORTADO = re.compile(
    r'^\s*(?:'
    r'[&*]'                    # âncora ou alias no começo da linha
    r'|---|\.\.\.'             # separador de documento
    r'|[^:#]*:\s*[|>]'         # bloco literal ou dobrado
    r'|[^:#]*:\s*[&*]\S'       # âncora ou alias no valor
    r'|[^:#]*:\s*\{'           # mapa em estilo de fluxo
    r')')


class YamlNaoSuportado(Exception):
    """Construção fora do subconjunto. Diz a linha e o que apareceu."""


def _escalar(bruto: str) -> Any:
    v = bruto.strip()
    if not v:
        return ''
    if v[0] in '"\'' and v[-1] == v[0] and len(v) > 1:
        return v[1:-1]
    if v.startswith('[') and v.endswith(']'):
        interno = v[1:-1].strip()
        return [_escalar(x) for x in interno.split(',')] if interno else []
    baixo = v.lower()
    if baixo in ('true', 'yes'):
        return True
    if baixo in ('false', 'no'):
        return False
    if baixo in ('null', '~'):
        return None
    if re.fullmatch(r'-?\d+', v):
        return int(v)
    if re.fullmatch(r'-?\d+\.\d+', v):
        return float(v)
    return v


def _linhas(texto: str) -> List[Tuple[int, int, str]]:
    saida = []
    for n, linha in enumerate(texto.splitlines(), start=1):
        sem_comentario = re.sub(r'\s+#.*$', '', linha) if '#' in linha else linha
        if not sem_comentario.strip() or sem_comentario.lstrip().startswith('#'):
            continue
        if _NAO_SUPORTADO.match(sem_comentario):
            raise YamlNaoSuportado(
                f'linha {n}: construção fora do subconjunto suportado '
                f'({sem_comentario.strip()[:40]!r}) — o leitor recusa em vez de adivinhar')
        recuo = len(sem_comentario) - len(sem_comentario.lstrip())
        saida.append((n, recuo, sem_comentario.strip()))
    return saida


def _bloco(linhas, i: int, recuo: int):
    """Lê o bloco cujo recuo é maior que `recuo`. Devolve (valor, próximo índice)."""
    if i >= len(linhas):
        return None, i

    if linhas[i][2].startswith('- '):
        itens = []
        while i < len(linhas) and linhas[i][1] == linhas[i][1] and \
                linhas[i][2].startswith('- ') and linhas[i][1] > recuo:
            n, rec, texto = linhas[i]
            resto = texto[2:].strip()
            if ':' in resto and not resto.startswith(('"', "'")):
                chave, _, valor = resto.partition(':')
                item = {}
                if valor.strip():
                    item[chave.strip()] = _escalar(valor)
                    i += 1
                else:
                    i += 1
                    filho, i = _bloco(linhas, i, rec + 2)
                    item[chave.strip()] = filho
                while i < len(linhas) and linhas[i][1] > rec and \
                        not linhas[i][2].startswith('- '):
                    n2, rec2, t2 = linhas[i]
                    c2, _, v2 = t2.partition(':')
                    if v2.strip():
                        item[c2.strip()] = _escalar(v2)
                        i += 1
                    else:
                        i += 1
                        filho, i = _bloco(linhas, i, rec2)
                        item[c2.strip()] = filho
                itens.append(item)
            else:
                itens.append(_escalar(resto))
                i += 1
        return itens, i

    mapa = {}
    base = linhas[i][1]
    while i < len(linhas) and linhas[i][1] == base:
        n, rec, texto = linhas[i]
        if texto.startswith('- '):
            break
        if ':' not in texto:
            raise YamlNaoSuportado(f'linha {n}: esperado `chave: valor`, veio '
                                   f'{texto[:40]!r}')
        chave, _, valor = texto.partition(':')
        if valor.strip():
            mapa[chave.strip()] = _escalar(valor)
            i += 1
        else:
            i += 1
            filho, i = _bloco(linhas, i, rec)
            mapa[chave.strip()] = filho if filho is not None else {}
    return mapa, i


def carregar(texto: str) -> Any:
    linhas = _linhas(texto)
    if not linhas:
        return {}
    valor, _ = _bloco(linhas, 0, -1)
    return valor
