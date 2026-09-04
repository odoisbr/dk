#!/usr/bin/env python3
"""Análise de similares: fonte com URL normalizada, evidência com procedência.

O que o código conclui aqui é procedência — fonte duplicada, fonte sem
observação, observação órfã, confiança não declarada. O julgamento sobre o que a
referência ensina é da skill."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import similares  # noqa: E402

errors = []


def projeto(fontes=(), evidencias=()):
    d = Path(tempfile.mkdtemp()) / 'p'
    (d / 'registry').mkdir(parents=True)
    (d / 'registry' / 'sources.json').write_text(
        json.dumps(list(fontes), ensure_ascii=False), encoding='utf-8')
    (d / 'registry' / 'evidence.json').write_text(
        json.dumps(list(evidencias), ensure_ascii=False), encoding='utf-8')
    return d


# ── normalização de URL: a mesma página não vira duas fontes ──
PARES = [
    ('https://exemplo.com/precos?utm_source=news&utm_campaign=x',
     'https://exemplo.com/precos'),
    ('EXEMPLO.com/Precos/', 'https://exemplo.com/Precos'),
    ('https://exemplo.com//precos', 'https://exemplo.com/precos'),
    ('https://exemplo.com:443/precos', 'https://exemplo.com/precos'),
    ('https://exemplo.com/p?b=2&a=1', 'https://exemplo.com/p?a=1&b=2'),
    ('https://exemplo.com/p?fbclid=abc', 'https://exemplo.com/p'),
]
for bruta, esperada in PARES:
    obtida = similares.normalizar_url(bruta)
    if obtida != esperada:
        errors.append(f'{bruta} → {obtida}, esperado {esperada}')

# caminho de arquivo não é URL e não deve ser tratado como uma
if similares.normalizar_url('0-apoio/cliente/Regras Gerais.md') != '':
    errors.append('caminho de arquivo não deveria virar URL')

# ── projeto vazio não é análise limpa ──
r = similares.avaliar(projeto())
if r['estado'] != 'por-comecar':
    errors.append(f"sem fonte de referência deu {r['estado']}")
if not any(a['id'] == 'SIM-SEM-FONTE' for a in r['achados']):
    errors.append('a ausência de referência deveria ser dita')

# ── duas fontes, a mesma página ──
FONTES = [
    {'id': 'SRC-001', 'title': 'Concorrente A — preços', 'type': 'concorrente',
     'path': 'https://a.com/precos?utm_source=news'},
    {'id': 'SRC-002', 'title': 'Concorrente A — preços (de novo)',
     'type': 'concorrente', 'path': 'https://A.com/precos/'},
    {'id': 'SRC-003', 'title': 'Referência B', 'type': 'referencia',
     'path': 'https://b.com/'},
    {'id': 'SRC-004', 'title': 'Ata da reunião', 'type': 'requisito-as-is',
     'path': '0-apoio/ata.md'},
]
EVIDENCIAS = [
    {'id': 'EVD-001', 'source_id': 'SRC-001', 'excerpt': 'preço em três planos',
     'location': 'https://a.com/precos', 'type': 'observacao',
     'confidence': 'alta'},
    {'id': 'EVD-002', 'source_id': 'SRC-009', 'excerpt': 'órfã',
     'location': 'x', 'type': 'observacao', 'confidence': 'media'},
    {'id': 'EVD-003', 'source_id': 'SRC-003', 'excerpt': 'sem confiança',
     'location': 'https://b.com/', 'type': 'observacao'},
]
r = similares.avaliar(projeto(FONTES, EVIDENCIAS))
ids = [a['id'] for a in r['achados']]

if 'SIM-DUPLICADA' not in ids:
    errors.append('SRC-001 e SRC-002 são a mesma página normalizada')
dup = [a for a in r['achados'] if a['id'] == 'SIM-DUPLICADA'][0]
if 'SRC-002' not in dup['evidencia']:
    errors.append(f"a duplicata não nomeia as fontes: {dup['evidencia']}")

if 'SIM-ORFA' not in ids:
    errors.append('EVD-002 aponta para SRC-009, que não existe')
if 'SIM-SEM-CONFIANCA' not in ids:
    errors.append('EVD-003 não declara confiança')
if 'SIM-SEM-EVIDENCIA' not in ids:
    errors.append('SRC-002 é referência sem nenhuma observação registrada')

# a ata não é referência de benchmark e não entra na conta
if any('SRC-004' in a['evidencia'] for a in r['achados']):
    errors.append('fonte que não é de benchmark não deveria ser cobrada aqui')
if r['totais']['fontes'] != 3:
    errors.append(f"fontes de benchmark contadas errado: {r['totais']}")

# ── a matriz diz "sem evidência", não zero ──
md = similares.matriz(projeto(FONTES, EVIDENCIAS))
if 'sem evidência' not in md:
    errors.append('ausência de evidência virou número na matriz')
if '0' == md.strip():
    errors.append('matriz vazia')
for esperado in ('SRC-001', 'SRC-003', 'Concorrente A'):
    if esperado not in md:
        errors.append(f'a matriz não traz {esperado}')

# ── toda conclusão declara quem decidiu ──
for a in r['achados']:
    if a.get('decidido_por') not in ('codigo', 'skill'):
        errors.append(f"{a['id']} não declara decidido_por")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
