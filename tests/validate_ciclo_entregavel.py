#!/usr/bin/env python3
"""O ciclo completo: insumo → registro → entregável formatado e válido.

Fecha o arco que a espinha abriu. O que a espinha grava em registro é o que
alimenta o documento que vai para o cliente."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import entregaveis, padrao, registry  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    for pasta in padrao.PASTAS:
        (projeto / pasta).mkdir(parents=True, exist_ok=True)
    (projeto / '0-apoio' / 'reunioes').mkdir(parents=True, exist_ok=True)
    insumo = projeto / '0-apoio' / 'reunioes' / '2026-08-14-convenios.md'
    insumo.write_text(
        'Reunião 14/08 — Convênios\n'
        'Fulana (gestora): o convênio não expira sozinho, quem tira do ar é o gestor.\n'
        'Beltrano: e quando o prazo vence?\n',
        encoding='utf-8')

    r = dk('levantar', '--projeto', str(projeto), '--insumo', str(insumo), '--apply')
    if r.returncode != 0:
        errors.append(f'levantar falhou: {r.stdout}{r.stderr}')

    regras = registry.carregar(projeto, 'regras')
    if not regras:
        errors.append('a espinha não gravou regra')

    linhas = ['## 1. Identificação', '',
              '| Campo | Valor |', '|---|---|',
              '| Projeto | Convênios |',
              '| Data e horário | 14/08/2026, 10:00 às 11:00 |',
              '', '## 2. Participantes', '',
              '| Nome | Papel |', '|---|---|', '| Fulana | gestora |', '',
              '## 3. Resumo Executivo', '',
              'Alinhamento sobre revogação de convênio.', '',
              '## 4. Tópicos Discutidos', '', '### Expiração', '',
              'Contexto discutido.', '',
              '## 5. Principais Decisões', '',
              '| Decisão | Contexto | Impacto |', '|---|---|---|']
    for reg in regras:
        linhas.append(f"| {reg['enunciado']} | {reg['fonte']} | a definir |")
    linhas += ['', '## 6. Encaminhamentos e Ações', '',
               '| Ação | Responsável | Prazo |', '|---|---|---|',
               '| Validar regra | Fulana | 20/08 |', '',
               '## 7. Pontos em Aberto / Pendências', '',
               'Nenhuma pendência registrada.', '']
    corpo = projeto / '0-apoio' / 'corpo-ata.md'
    corpo.write_text('\n'.join(linhas), encoding='utf-8')

    achados = entregaveis.validar('ata', corpo.read_text(encoding='utf-8'))
    if achados:
        errors.append(f'o corpo montado deveria passar no contrato: {achados}')

    e = dk('entregar', '--projeto', str(projeto), '--tipo', 'ata',
           '--corpo', str(corpo), '--apply')
    if e.returncode != 0:
        errors.append(f'entregar falhou: {e.stdout}{e.stderr}')

    gerados = list((projeto / padrao.destino('ata')).glob('*.html'))
    if not gerados:
        errors.append('nenhum entregável gerado')
    else:
        html = gerados[0].read_text(encoding='utf-8')
        for esperado in ('Ata de Reunião', 'Fulana', '@font-face', '<table'):
            if esperado not in html:
                errors.append(f'{esperado!r} ausente do entregável')
        if regras and regras[0]['enunciado'][:30] not in html:
            errors.append('a regra do registro não chegou ao entregável')

    if 4 in {a['regra'] for a in padrao.verificar(projeto)}:
        errors.append('há insumo e ata; a regra 4 não deveria reprovar')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
