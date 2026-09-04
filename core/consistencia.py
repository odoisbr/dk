#!/usr/bin/env python3
"""Os seis tipos de inconsistência do community, mais um que a realidade acrescentou.

Os seis vieram do `validar-consistencia-requisitos`. O sétimo — TÍTULO-TRUNCADO —
saiu de rodar contra um projeto vivo: 40 de 86 requisitos tinham o rótulo cortado,
e cinco ficaram com o mesmo prefixo. Um rótulo cortado engana a leitura humana e
engana comparação automática.

A divisão de trabalho é explícita em cada achado, no campo `decidido_por`:

    codigo  a verificação é determinística e o achado é conclusão
    skill   o código marca o candidato e a decisão exige leitura

Fingir determinismo onde não há é pior que não ter a checagem: produz achado
falso com cara de fato.

Limite lexical, declarado de propósito: `_ACOES`, `_VAGOS` e `_MENSURAVEL` são
listas fixas em português. Requisito escrito em outro idioma, ou com verbo fora
da lista, não é reconhecido como ação — e a comparação cai no caminho sem filtro
de ação, que erra para o lado do falso positivo. Isso é escolha, não descuido: o
filtro de ação só pesa em par parecido — par de texto idêntico é duplicata com ou
sem ele —, e todo par parecido sai com `decidido_por: skill`, ou seja, vai para
leitura humana em vez de virar conclusão. O limite lexical produz candidato a
mais, nunca conclusão errada. Ampliar a lista é barato e não muda contrato;
trocá-la por stemmer traria dependência, que o pacote não tem."""
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
    'TITULO-TRUNCADO': 'o rótulo do item está cortado e não representa o conteúdo',
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


# Num requisito, o verbo é o requisito. "incluir dependentes" e "remover
# dependentes" compartilham quase todos os substantivos e são opostos — tratar
# isso como duplicata é o erro mais fácil de cometer numa lista de CRUD.
_ACOES = {
    'incluir', 'inserir', 'adicionar', 'cadastrar', 'criar', 'registrar',
    'remover', 'excluir', 'apagar', 'deletar', 'cancelar', 'revogar',
    'editar', 'alterar', 'atualizar', 'modificar', 'corrigir',
    'consultar', 'listar', 'visualizar', 'exibir', 'buscar', 'pesquisar',
    'aprovar', 'rejeitar', 'reprovar', 'validar', 'bloquear', 'desbloquear',
    'renovar', 'importar', 'exportar', 'gerar', 'imprimir', 'enviar',
}


def _acoes(texto: str) -> set:
    return _tokens(texto) & {_normaliza(a) for a in _ACOES}


def _similaridade(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    # Ações diferentes ⇒ requisitos diferentes, por mais que o resto coincida.
    aa, ab = _acoes(a), _acoes(b)
    if aa and ab and not (aa & ab):
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _texto(item: dict) -> str:
    """O texto mais completo que o item tem.

    Num projeto real, 40 de 86 requisitos tinham `title` truncado — cortado no
    ponto de "cat. 40" — e cinco deles ficaram com o mesmo prefixo. Comparar por
    `title` acusou cinco duplicatas que não existiam; a `description` mostrava
    cinco requisitos distintos. Compare pelo campo mais completo, sempre."""
    for campo in ('description', 'descricao', 'titulo', 'title', 'enunciado'):
        valor = (item.get(campo) or '').strip()
        if valor:
            return valor
    return ''


def _truncado(item: dict) -> bool:
    """`title` visivelmente cortado: termina em reticência, ou a `description`
    é bem maior e começa pelo mesmo texto."""
    titulo = (item.get('title') or item.get('titulo') or '').strip()
    descricao = (item.get('description') or item.get('descricao') or '').strip()
    if not titulo:
        return False
    if titulo.endswith(('…', '...')):
        return True
    return bool(descricao) and descricao.startswith(titulo) \
        and len(descricao) > len(titulo) + 20


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

    # Tipo 3 — ÓRFÃO: requisito sem âncora rastreável.
    #
    # A âncora depende do esquema, e a regra vale nos dois sem precisar saber
    # qual é. No canônico a âncora é `sources` — requisito e regra são irmãos,
    # ambos presos ao documento de origem. No esquema do DK é `deriva_de`.
    # Ter qualquer uma das duas basta; não ter nenhuma é que é órfão.
    #
    # A versão anterior olhava só `deriva_de` e marcou os 86 requisitos de um
    # projeto real como órfãos — todos tinham fonte.
    for q in requisitos:
        origem = q.get('deriva_de')
        fontes = q.get('sources') or []
        if origem and origem in ids_regras:
            continue
        if fontes:
            continue
        if origem:
            evidencia = (f"{q['id']} aponta para {origem!r}, que não existe em "
                         'regras, e não declara fonte')
        else:
            evidencia = (f"{q['id']} não tem vínculo com regra nem fonte "
                         'declarada — nada diz de onde ele veio')
        achados.append(_achado('ORFAO', [q['id']], evidencia,
                               'RESOLVE-ANTES-DO-DESIGN', 'codigo'))

    # TÍTULO-TRUNCADO: rótulo cortado engana leitura humana e comparação automática
    truncados = [q['id'] for q in requisitos if _truncado(q)]
    if truncados:
        achados.append(_achado(
            'TITULO-TRUNCADO', truncados,
            f'{len(truncados)} requisito(s) com título cortado, entre eles '
            + ', '.join(truncados[:5])
            + ' — o rótulo não representa o conteúdo, e quem lê a lista não vê '
              'o requisito inteiro',
            'PODE-POSTERGAR', 'codigo'))

    # Tipo 2 — DUPLICATA
    for i in range(len(requisitos)):
        for j in range(i + 1, len(requisitos)):
            a, b = requisitos[i], requisitos[j]
            s = _similaridade(_texto(a), _texto(b))
            if s >= 0.6:
                # Texto idêntico o código conclui. Parecido, não: num projeto
                # real, "credencial de Aposentado" e "credencial de Estagiário"
                # deram 82% — são variantes paramétricas da mesma regra, e
                # decidir se viram um requisito só exige ler o domínio.
                identico = s >= 0.999
                achados.append(_achado(
                    'DUPLICATA', [a['id'], b['id']],
                    f"similaridade {s:.0%} entre {a['id']} e {b['id']}: "
                    f"{_texto(a)[:45]!r} × {_texto(b)[:45]!r}"
                    + ('' if identico else
                       ' — parecidos, não idênticos: pode ser variante '
                       'paramétrica, e quem julga é a skill'),
                    'RESOLVE-ANTES-DO-DESIGN',
                    'codigo' if identico else 'skill'))

    # Tipo 5 — NF-SEM-CRITÉRIO
    for q in requisitos:
        titulo = _texto(q)
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
    definidos = ' '.join([_texto(r) for r in regras]
                         + [_texto(q) for q in requisitos])
    for q in requisitos:
        for nome in re.findall(r'\b(?:Portal|Sistema|Módulo|Modulo|API)\s+'
                               r'([A-ZÀ-Ú][\wÀ-ú]+)', _texto(q)):
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
            s = _similaridade(_texto(a), _texto(b))
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
