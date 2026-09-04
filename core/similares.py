#!/usr/bin/env python3
"""Análise de similares: referência externa com procedência, não com opinião.

O Kit tinha 35 skills `sea-similar-*` — intake, site-mapper, screen-inventory,
visual-dna, report e por aí. Quase todas eram passo de um mesmo fluxo. O que
sobrevive aqui é o que só código faz bem: normalizar a URL para a mesma página
não virar duas fontes, e cobrar procedência entre fonte e observação.

O julgamento — o que a referência ensina, o que copiar seria plágio, que padrão
se repete — é da skill, e sai marcado como tal.

A forma dos registros é a que os projetos da casa usam: `sources.json` com `id`,
`title`, `type` e `path`; `evidence.json` com `id`, `source_id`, `excerpt`,
`location`, `type` e `confidence`. Nada de esquema novo para benchmark."""
from __future__ import annotations
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from core import registry

# Os três papéis do benchmark. `antirreferencia` é o que se estuda para não
# repetir — some das análises que só listam concorrente, e é o mais citado
# quando alguém pergunta por que uma decisão foi tomada.
PAPEIS = ('referencia', 'concorrente', 'antirreferencia')

# Parâmetro que muda a URL sem mudar a página. Sem isso, a mesma tela entra três
# vezes no comparativo porque veio de três campanhas.
_RASTREIO = {'fbclid', 'gclid', 'msclkid', 'ref', 'source'}


def normalizar_url(url: str) -> str:
    """A URL reduzida ao que identifica a página. String vazia se não for URL.

    Caminho de arquivo do projeto não é URL: devolver algo aqui faria a ata da
    reunião competir com o site do concorrente na deduplicação."""
    bruta = (url or '').strip()
    if not bruta:
        return ''
    if not re.match(r'^https?://', bruta, re.I):
        if not re.match(r'^[\w-]+(\.[\w-]+)+(/|$|:)', bruta):
            return ''
        bruta = 'https://' + bruta
    p = urllib.parse.urlsplit(bruta)
    esquema = p.scheme.lower()
    host = (p.hostname or '').lower()
    if not host:
        return ''
    porta = p.port
    rede = host
    if porta and not ((esquema == 'http' and porta == 80)
                      or (esquema == 'https' and porta == 443)):
        rede += f':{porta}'
    caminho = re.sub(r'/+', '/', p.path or '/')
    if caminho != '/' and caminho.endswith('/'):
        caminho = caminho[:-1]
    consulta = [(k, v) for k, v in
                urllib.parse.parse_qsl(p.query, keep_blank_values=True)
                if not k.lower().startswith('utm_')
                and k.lower() not in _RASTREIO]
    consulta.sort()
    if caminho == '/':
        caminho = ''
    return urllib.parse.urlunsplit(
        (esquema, rede, caminho, urllib.parse.urlencode(consulta), ''))


def _achado(ident, titulo, evidencia, impacto='medio', decidido='codigo') -> Dict:
    return {'id': ident, 'titulo': titulo, 'evidencia': evidencia,
            'impacto': impacto, 'decidido_por': decidido}


def fontes(raiz: Path) -> List[dict]:
    """Só as fontes de benchmark. Ata e documento do cliente não entram."""
    return [f for f in registry.carregar(raiz, 'fontes')
            if str(f.get('type', '')).lower() in PAPEIS]


def avaliar(raiz: Path) -> Dict:
    raiz = Path(raiz)
    refs = fontes(raiz)
    evidencias = registry.carregar(raiz, 'evidencias')
    achados: List[Dict] = []

    if not refs:
        achados.append(_achado(
            'SIM-SEM-FONTE', 'nenhuma referência registrada',
            'sources.json não tem fonte com type ' + ', '.join(PAPEIS)
            + ' — a análise de similares não está incompleta, está por começar',
            impacto='alto'))
        return {'estado': 'por-comecar', 'fontes': [],
                'totais': {'fontes': 0, 'evidencias': 0}, 'achados': achados}

    ids = {f.get('id') for f in refs}
    por_url = defaultdict(list)
    for f in refs:
        chave = normalizar_url(f.get('path') or f.get('url') or '')
        if chave:
            por_url[chave].append(f.get('id'))
    for url, grupo in sorted(por_url.items()):
        if len(grupo) > 1:
            achados.append(_achado(
                'SIM-DUPLICADA', 'a mesma página em mais de uma fonte',
                f"{', '.join(sorted(grupo))} apontam para {url} — "
                'a comparação conta a mesma referência duas vezes'))

    com_evidencia = defaultdict(list)
    for e in evidencias:
        alvo = e.get('source_id')
        if alvo in ids:
            com_evidencia[alvo].append(e)
        elif alvo and alvo not in {f.get('id')
                                   for f in registry.carregar(raiz, 'fontes')}:
            achados.append(_achado(
                'SIM-ORFA', 'observação sem fonte',
                f"{e.get('id', '?')} aponta para {alvo}, que não existe em "
                'sources.json', impacto='alto'))
        if alvo in ids and not e.get('confidence'):
            achados.append(_achado(
                'SIM-SEM-CONFIANCA', 'observação sem confiança declarada',
                f"{e.get('id', '?')} não diz o quanto se pode confiar nela — "
                'observação de referência é leitura, e leitura erra'))

    for f in refs:
        if not com_evidencia.get(f.get('id')):
            achados.append(_achado(
                'SIM-SEM-EVIDENCIA', 'referência sem nenhuma observação',
                f"{f.get('id')} ({f.get('title', '')}) está na lista e não "
                'produziu nada — ausência de evidência, não nota zero'))

    return {
        'estado': 'em-andamento',
        'fontes': [{'id': f.get('id'), 'title': f.get('title', ''),
                    'type': f.get('type'),
                    'url': normalizar_url(f.get('path') or ''),
                    'evidencias': len(com_evidencia.get(f.get('id'), []))}
                   for f in refs],
        'totais': {'fontes': len(refs),
                   'evidencias': sum(len(v) for v in com_evidencia.values())},
        'achados': achados,
    }


def matriz(raiz: Path) -> str:
    """O comparativo em Markdown. Fonte sem observação diz isso, e não zero."""
    r = avaliar(raiz)
    if r['estado'] == 'por-comecar':
        return ('# Análise de similares\n\nNenhuma referência registrada.\n')
    linhas = ['# Análise de similares', '',
              f"{r['totais']['fontes']} referências · "
              f"{r['totais']['evidencias']} observações", '',
              '| Fonte | Papel | Página | Observações |', '|---|---|---|---|']
    for f in r['fontes']:
        quantas = (f'{f["evidencias"]}' if f['evidencias']
                   else 'sem evidência')
        linhas.append(f"| {f['id']} — {f['title']} | {f['type']} | "
                      f"{f['url'] or '—'} | {quantas} |")
    return '\n'.join(linhas) + '\n'
