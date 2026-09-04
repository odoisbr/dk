#!/usr/bin/env python3
"""O deck 16:9: dez tipos, limite avisado, autocontido."""
from __future__ import annotations
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import deck, marca  # noqa: E402

errors = []

for tipo in ('capa', 'bullets', 'destaque', 'tabela', 'comparacao', 'metricas',
             'fluxo', 'imagem', 'split', 'secao', 'encerramento'):
    if tipo not in deck.TIPOS:
        errors.append(f'tipo de slide ausente: {tipo}')

SLIDES = [
    {'tipo': 'capa', 'titulo': 'Credenciamento', 'sub': 'SESC-DF',
     'kicker': 'Entrega', 'data': '04/09/2026'},
    {'tipo': 'bullets', 'titulo': 'O que entra',
     'bullets': ['Renovação de credencial', 'Mudança de tipo', 'Meus dados']},
    {'tipo': 'metricas', 'titulo': 'Números',
     'metricas': [{'valor': '86', 'rotulo': 'requisitos'},
                  {'valor': '18', 'rotulo': 'regras'}]},
    {'tipo': 'tabela', 'titulo': 'Perfis', 'colunas': ['Perfil', 'Pode'],
     'linhas': [['GEREL', 'aprovar'], ['Titular', 'solicitar']]},
    {'tipo': 'comparacao', 'titulo': 'Antes e depois',
     'esquerda': {'titulo': 'Hoje', 'itens': ['manual']},
     'direita': {'titulo': 'Depois', 'itens': ['automático']}},
    {'tipo': 'encerramento', 'titulo': 'Obrigado!'},
]

if deck.validar(SLIDES):
    errors.append(f'deck válido não deveria ter achado: {deck.validar(SLIDES)}')

if 'DECK-SEM-TIPO' not in {a['id'] for a in deck.validar([{'titulo': 'x'}])}:
    errors.append('slide sem tipo deveria reprovar')

if 'DECK-TIPO-DESCONHECIDO' not in {
        a['id'] for a in deck.validar([{'tipo': 'carrossel', 'titulo': 'x'}])}:
    errors.append('tipo inexistente deveria reprovar')

if 'DECK-CAMPO' not in {a['id'] for a in
                        deck.validar([{'tipo': 'bullets', 'titulo': 'x'}])}:
    errors.append('bullets sem a lista deveria reprovar')

cheio = deck.validar([{'tipo': 'bullets', 'titulo': 'x',
                       'bullets': [f'item {i}' for i in range(12)]}])
ach = [a for a in cheio if a['id'] == 'DECK-OVERFLOW']
if not ach:
    errors.append('12 bullets passam do limite e o aviso não veio')
elif ach[0]['impacto'] != 'medio':
    errors.append('overflow avisa, não bloqueia — a altura é fixa, não é erro')

html = deck.montar({'titulo': 'Credenciamento', 'cliente': 'SESC-DF'}, SLIDES)
if html.count('class="slide"') != len(SLIDES):
    errors.append(f"{html.count('class=')} blocos para {len(SLIDES)} slides")
if '@font-face' not in html:
    errors.append('deck sem fontes embutidas')
if re.search(r'(?:src|href)\s*=\s*"https?://', html):
    errors.append('deck faz requisição externa; deveria ser autocontido')
if marca.CORES['blue'] not in html:
    errors.append('a marca não foi aplicada')
if str(deck.LARGURA) not in html or str(deck.ALTURA) not in html:
    errors.append('o slide não declara a proporção 16:9')
if 'Credenciamento' not in html or 'SESC-DF' not in html:
    errors.append('capa sem título ou cliente')

# marcação inline do modelo original
negrito = deck.montar({'titulo': 't'},
                      [{'tipo': 'bullets', 'titulo': 'x',
                        'bullets': ['um **forte** e uma\\nquebra']}])
if '<strong>forte</strong>' not in negrito:
    errors.append('negrito inline não convertido')
if '<br>' not in negrito:
    errors.append('quebra de linha não convertida')

# escape: conteúdo de cliente não pode injetar marcação
escapado = deck.montar({'titulo': 't'},
                       [{'tipo': 'bullets', 'titulo': 'x',
                         'bullets': ['<script>alert(1)</script>']}])
if '<script>' in escapado:
    errors.append('conteúdo não escapado: marcação do conteúdo virou HTML')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
