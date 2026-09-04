#!/usr/bin/env python3
"""O gate bloqueia com o furo aberto e libera quando ele fecha.

Prova que o gate mede o estado do projeto, e não uma flag de aprovação. É o que
faz o handoff valer alguma coisa: ele não é um carimbo, é uma medição."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import entregaveis, io, padrao, prontidao, registry  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


COMPLETO = ('o gestor com perfil de acesso revoga o convênio; o objetivo é '
            'reduzir o indicador de vencidos; escopo restrito ao módulo; '
            'integra com o portal; migra dado do cadastro atual; hoje é '
            'planilha; prazo e restrição legal definidos; usuário gestor')

with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    for pasta in padrao.PASTAS:
        (projeto / pasta).mkdir(parents=True, exist_ok=True)

    # estado 1: furo aberto — regra sem requisito
    registry.gravar(projeto, 'regras', [
        {'id': 'RN-001', 'enunciado': COMPLETO, 'citacao': 'quem tira é o gestor'},
        {'id': 'RN-099', 'enunciado': 'revogado não reativa'},
    ])
    registry.gravar(projeto, 'requisitos', [
        {'id': 'REQ-001', 'titulo': COMPLETO, 'deriva_de': 'RN-001'},
    ])

    r1 = prontidao.avaliar(projeto)
    if r1['pronto']:
        errors.append('com RN-099 órfã o gate não deveria abrir')
    bloqueados = {i['nome'] for i in r1['bloqueios']}
    if 'cobertura' not in bloqueados:
        errors.append(f'cobertura deveria bloquear: {bloqueados}')
    if 'entregaveis' not in bloqueados:
        errors.append('sem entregável gerado, o item entregaveis deveria bloquear')

    cli1 = dk('handoff', '--projeto', str(projeto))
    if cli1.returncode == 0:
        errors.append('a CLI deveria reprovar com o gate fechado')

    # estado 2: furo fechado — requisito derivado e entregável gerado
    registry.gravar(projeto, 'requisitos', [
        {'id': 'REQ-001', 'titulo': COMPLETO, 'deriva_de': 'RN-001'},
        {'id': 'REQ-002', 'titulo': 'convênio revogado não pode ser reativado',
         'deriva_de': 'RN-099'},
    ])
    io.atomic_write(
        projeto / padrao.destino('requisitos') / 'requisitos-2026-09-04.html',
        '<p>REQ-001 e REQ-002 constam</p>')

    r2 = prontidao.avaliar(projeto)
    if not r2['pronto']:
        nomes = [(i['nome'], i['evidencia']) for i in r2['bloqueios']]
        errors.append(f'com o furo fechado o gate deveria abrir: {nomes}')

    cli2 = dk('handoff', '--projeto', str(projeto))
    if cli2.returncode != 0:
        errors.append(f'a CLI deveria liberar: {cli2.stdout}')
    if 'gate aberto' not in cli2.stdout:
        errors.append('a CLI não anunciou o gate aberto')

    # o pacote sai, com a matriz substituída a partir do registro
    secoes = entregaveis.CONTRATOS['handoff']['secoes']
    corpo = []
    for i, nome in enumerate(secoes, start=1):
        corpo.append(f'## {i}. {nome}\n')
        corpo.append('{{RASTREABILIDADE}}\n' if nome == 'Rastreabilidade'
                     else 'conteúdo da seção.\n')
    arq = projeto / '0-apoio' / 'corpo-handoff.md'
    io.atomic_write(arq, '\n'.join(corpo))

    ap = dk('handoff', '--projeto', str(projeto), '--corpo', str(arq), '--apply')
    if ap.returncode != 0:
        errors.append(f'gerar o pacote falhou: {ap.stdout}{ap.stderr}')

    gerados = list((projeto / padrao.destino('handoff')).glob('handoff-*.html'))
    if not gerados:
        errors.append('o pacote não foi gravado')
    else:
        html = gerados[0].read_text(encoding='utf-8')
        if '{{RASTREABILIDADE}}' in html:
            errors.append('o marcador não foi substituído pela matriz')
        for esperado in ('REQ-001', 'REQ-002', 'RN-099', 'rastreado',
                         'Handoff para Desenvolvimento', '@font-face'):
            if esperado not in html:
                errors.append(f'{esperado!r} ausente do pacote')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
