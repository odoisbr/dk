#!/usr/bin/env python3
"""Os entregáveis de comunicação, ponta a ponta.

Manual, e-mail e apresentação gerados num projeto, com as três garantias que
importam: contrato respeitado, arquivo autocontido, e credencial nunca escrita."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import entregaveis, io, padrao  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


def corpo_de(tipo: str) -> str:
    return '\n'.join(f'## {i}. {nome}\n\nconteúdo da seção.\n' for i, nome
                     in enumerate(entregaveis.CONTRATOS[tipo]['secoes'], start=1))


DECK = {
    'meta': {'titulo': 'Credenciamento', 'cliente': 'SESC-DF', 'serie': 'Entrega'},
    'slides': [
        {'tipo': 'capa', 'kicker': 'Entrega', 'titulo': 'Credenciamento',
         'sub': 'SESC-DF', 'data': '04/09/2026'},
        {'tipo': 'metricas', 'titulo': 'Escopo',
         'metricas': [{'valor': '86', 'rotulo': 'requisitos'},
                      {'valor': '18', 'rotulo': 'regras de negócio'}]},
        {'tipo': 'encerramento'},
    ],
}

with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    for pasta in padrao.PASTAS:
        (projeto / pasta).mkdir(parents=True, exist_ok=True)
    apoio = projeto / '0-apoio'

    # manual
    io.atomic_write(apoio / 'corpo-manual.md', corpo_de('manual'))
    r = dk('entregar', '--projeto', str(projeto), '--tipo', 'manual',
           '--corpo', str(apoio / 'corpo-manual.md'), '--apply')
    if r.returncode != 0:
        errors.append(f'manual falhou: {r.stdout}{r.stderr}')
    manuais = list((projeto / entregaveis.destino('manual')).glob('manual-*.html'))
    if not manuais:
        errors.append('manual não foi gravado')
    elif '@font-face' not in manuais[0].read_text(encoding='utf-8'):
        errors.append('manual não é autocontido')

    # e-mail com o assunto no padrão
    email = corpo_de('email').replace('## 1. Assunto',
                                      '## 1. Assunto: (Entrega) Credenciamento')
    io.atomic_write(apoio / 'corpo-email.md', email)
    r = dk('entregar', '--projeto', str(projeto), '--tipo', 'email',
           '--corpo', str(apoio / 'corpo-email.md'), '--apply')
    if r.returncode != 0:
        errors.append(f'e-mail falhou: {r.stdout}{r.stderr}')

    # e-mail com credencial preenchida: tem que bloquear
    vazando = email + '\nDADOS DE ACESSO\nUsuário: admin\nSenha: sesc2026\n'
    io.atomic_write(apoio / 'corpo-email-vazando.md', vazando)
    r = dk('entregar', '--projeto', str(projeto), '--tipo', 'email',
           '--corpo', str(apoio / 'corpo-email-vazando.md'), '--apply')
    if r.returncode == 0:
        errors.append('VAZAMENTO: e-mail com senha foi gerado')
    if 'EMA-CREDENCIAL' not in r.stdout:
        errors.append('o bloqueio não citou a regra da credencial')
    gerados = list((projeto / entregaveis.destino('email')).glob('email-*.html'))
    for g in gerados:
        if 'sesc2026' in g.read_text(encoding='utf-8'):
            errors.append('VAZAMENTO: a senha chegou ao arquivo gerado')

    # apresentação
    io.atomic_write(apoio / 'deck.json', json.dumps(DECK, ensure_ascii=False))
    r = dk('entregar', '--projeto', str(projeto), '--tipo', 'apresentacao',
           '--corpo', str(apoio / 'deck.json'), '--apply')
    if r.returncode != 0:
        errors.append(f'apresentação falhou: {r.stdout}{r.stderr}')
    decks = list((projeto / entregaveis.destino('apresentacao'))
                 .glob('apresentacao-*.html'))
    if not decks:
        errors.append('deck não foi gravado')
    else:
        html = decks[0].read_text(encoding='utf-8')
        if html.count('class="slide"') != len(DECK['slides']):
            errors.append('o deck não tem um bloco por slide')
        for esperado in ('Credenciamento', 'SESC-DF', '86', '@font-face'):
            if esperado not in html:
                errors.append(f'{esperado!r} ausente do deck')

    # apresentação com slide inválido: bloqueia
    ruim = {'meta': {}, 'slides': [{'tipo': 'bullets', 'titulo': 'sem lista'}]}
    io.atomic_write(apoio / 'deck-ruim.json', json.dumps(ruim))
    r = dk('entregar', '--projeto', str(projeto), '--tipo', 'apresentacao',
           '--corpo', str(apoio / 'deck-ruim.json'), '--apply')
    if r.returncode == 0:
        errors.append('slide sem campo obrigatório deveria bloquear')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
