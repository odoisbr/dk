#!/usr/bin/env python3
"""O handoff só sai com o pipeline fechado.

O gate não inventa verificação: ele cobra, de uma vez, as que as etapas
anteriores já fazem. Cada bloqueio diz qual etapa resolve e qual comando rodar."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, padrao, prontidao, registry  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'o gestor revoga o convênio'},
        {'id': 'RN-099', 'enunciado': 'revogado não reativa'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'revogação manual pelo gestor',
         'deriva_de': 'RN-001'},
    ])

    r = prontidao.avaliar(raiz)

    if r['pronto']:
        errors.append('projeto com regra órfã e lacunas não deveria estar pronto')
    if not r['bloqueios']:
        errors.append('nenhum bloqueio num projeto com furo')

    nomes = {i['nome'] for i in r['itens']}
    for esperado in ('cobertura', 'consistencia', 'lacunas', 'padrao',
                     'prototipo', 'entregaveis'):
        if esperado not in nomes:
            errors.append(f'o gate não cobra {esperado}')

    for i in r['itens']:
        for campo in ('nome', 'estado', 'evidencia', 'resolve_em', 'comando'):
            if campo not in i:
                errors.append(f"{i.get('nome')}: item do gate sem {campo}")
        if i['estado'] not in ('ok', 'bloqueio', 'aviso'):
            errors.append(f"{i['nome']}: estado inválido {i['estado']!r}")

    cob = [i for i in r['itens'] if i['nome'] == 'cobertura'][0]
    if cob['estado'] != 'bloqueio':
        errors.append('regra órfã deveria bloquear a cobertura')
    if 'RN-099' not in cob['evidencia']:
        errors.append(f"a evidência não nomeia a regra órfã: {cob['evidencia']}")
    if 'entender' not in cob['resolve_em']:
        errors.append('o bloqueio de cobertura deveria apontar a etapa entender')
    if 'dk entender' not in cob['comando']:
        errors.append('o bloqueio deveria dar o comando que resolve')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001',
         'enunciado': 'o gestor com perfil de acesso revoga o convênio; '
                      'objetivo é reduzir o indicador de vencidos; escopo '
                      'restrito ao módulo; integra com o portal; migra dado '
                      'do cadastro atual; hoje é planilha; prazo definido'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001',
         'titulo': 'revogação manual pelo gestor com perfil de acesso; '
                   'objetivo, escopo, integração, dado migrado e prazo definidos; '
                   'usuario gestor; hoje planilha',
         'deriva_de': 'RN-001'},
    ])
    io.atomic_write(raiz / padrao.destino('requisitos') / 'requisitos-2026-09-04.html',
                    '<p>REQ-001</p>')

    r = prontidao.avaliar(raiz)
    cob = [i for i in r['itens'] if i['nome'] == 'cobertura'][0]
    if cob['estado'] == 'bloqueio':
        errors.append(f"cobertura fechada não deveria bloquear: {cob['evidencia']}")
    ent = [i for i in r['itens'] if i['nome'] == 'entregaveis'][0]
    if ent['estado'] == 'bloqueio':
        errors.append(f"requisito no entregável não deveria bloquear: "
                      f"{ent['evidencia']}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
