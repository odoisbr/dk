#!/usr/bin/env python3
"""Escrever num projeto que já tem registro canônico não pode estragá-lo.

É o teste do único caminho em que o DK pode causar dano real: gravar sobre o
registro de um projeto vivo. Ele reproduz o que aconteceu ao rodar sobre o
Credenciamento SESC-DF e cobra as quatro garantias que faltavam.

Fixture com a forma do registro real — `business-rules.json`, `requirements.json`,
`id-counters.json` — e ids já em uso, que é o que fazia a versão anterior
escrever por cima."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, padrao, registry  # noqa: E402

errors = []

REGRAS = [
    {'id': 'RN-001', 'title': 'Validade por subcategoria',
     'description': 'Aposentado: 2 anos a partir do credenciamento.',
     'status': 'vigente', 'sources': ['SRC-015']},
    {'id': 'RN-002', 'title': 'Bloqueio de titular falecido',
     'description': 'O titular falecido muda para a categoria 25.',
     'status': 'vigente', 'sources': ['SRC-015']},
]
REQUISITOS = [
    {'id': 'RF-001', 'title': 'Alterar categoria do titular',
     'description': 'O Administrador GEREL altera a categoria do titular.',
     'type': 'funcional', 'status': 'especificado', 'priority': 'Essencial',
     'sources': ['SRC-015'], 'version': '10'},
]
CONTADORES = {'SRC': 21, 'RF': 1, 'RN': 2}

INSUMO = ('Reunião 04/09 — Credenciamento\n'
          'Mariana (gestora): o titular falecido não pode ter credencial renovada.\n'
          'Angelo: o dependente continua, mas muda de categoria.\n')


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    for pasta in padrao.PASTAS:
        (projeto / pasta).mkdir(parents=True, exist_ok=True)
    (projeto / '0-apoio' / 'reunioes').mkdir(parents=True, exist_ok=True)
    io.atomic_json(projeto / 'registry' / 'business-rules.json', REGRAS)
    io.atomic_json(projeto / 'registry' / 'requirements.json', REQUISITOS)
    io.atomic_json(projeto / 'registry' / 'id-counters.json', CONTADORES)
    insumo = projeto / '0-apoio' / 'reunioes' / '2026-09-04-alinhamento.md'
    insumo.write_text(INSUMO, encoding='utf-8')

    if registry.esquema(projeto) != 'canonico':
        errors.append('a fixture deveria ser reconhecida como canônica')

    r = dk('levantar', '--projeto', str(projeto), '--insumo', str(insumo), '--apply')
    if r.returncode != 0:
        errors.append(f'levantar falhou: {r.stdout}{r.stderr}')

    br = json.loads((projeto / 'registry' / 'business-rules.json').read_text(
        encoding='utf-8'))
    rq = json.loads((projeto / 'registry' / 'requirements.json').read_text(
        encoding='utf-8'))
    ct = json.loads((projeto / 'registry' / 'id-counters.json').read_text(
        encoding='utf-8'))

    # 1. nenhum registro paralelo ao lado do canônico
    paralelos = [f.name for f in (projeto / 'registry').glob('*.json')
                 if f.name in ('regras.json', 'requisitos.json')]
    if paralelos:
        errors.append(f'registro paralelo criado: {paralelos} — é a árvore '
                      'dupla que o DK existe para impedir')

    # 2. o que já existia sai intacto, campo por campo
    for original in REGRAS:
        atual = [x for x in br if x['id'] == original['id']]
        if not atual:
            errors.append(f"{original['id']} sumiu do registro")
        elif atual[0] != original:
            errors.append(f"{original['id']} foi alterado: {atual[0]}")
    for original in REQUISITOS:
        atual = [x for x in rq if x['id'] == original['id']]
        if not atual or atual[0] != original:
            errors.append(f"{original['id']} foi alterado ou sumiu")

    # 3. id novo continua do contador, não colide com o que existe
    novos_rn = [x['id'] for x in br if x['id'] not in {r['id'] for r in REGRAS}]
    if not novos_rn:
        errors.append('nenhuma regra nova foi gravada')
    for ident in novos_rn:
        if int(ident.split('-')[1]) <= CONTADORES['RN']:
            errors.append(f'{ident} reaproveitou faixa de id já em uso')
    novos_rf = [x['id'] for x in rq if x['id'] not in {q['id'] for q in REQUISITOS}]
    for ident in novos_rf:
        if not ident.startswith('RF-'):
            errors.append(f'requisito novo fora do prefixo do projeto: {ident}')
        if int(ident.split('-')[1]) <= CONTADORES['RF']:
            errors.append(f'{ident} reaproveitou faixa de id já em uso')

    # 4. o contador avança para os dois prefixos, não só para o último
    if ct.get('RN', 0) <= CONTADORES['RN']:
        errors.append(f"contador RN não avançou: {ct.get('RN')} — a segunda "
                      'atualização estava desfazendo a primeira')
    if ct.get('RF', 0) <= CONTADORES['RF']:
        errors.append(f"contador RF não avançou: {ct.get('RF')}")
    if ct.get('SRC') != CONTADORES['SRC']:
        errors.append('contador de outro prefixo foi alterado sem motivo')

    # 5. item novo sai na forma do esquema do projeto, não na do DK
    for item in br:
        if item['id'] in novos_rn:
            if 'title' not in item or 'status' not in item:
                errors.append(f'{item["id"]} sem a forma canônica: {item}')
            for interno in ('enunciado', 'citacao', 'titulo', 'fonte'):
                if interno in item:
                    errors.append(f'{item["id"]} levou campo interno do DK: '
                                  f'{interno}')

    # 6. rodar de novo com o mesmo insumo não cria nada
    antes = len(br), len(rq)
    r2 = dk('levantar', '--projeto', str(projeto), '--insumo', str(insumo), '--apply')
    if r2.returncode != 0:
        errors.append(f'segunda execução falhou: {r2.stdout}{r2.stderr}')
    depois = (len(json.loads((projeto / 'registry' / 'business-rules.json')
                             .read_text(encoding='utf-8'))),
              len(json.loads((projeto / 'registry' / 'requirements.json')
                             .read_text(encoding='utf-8'))))
    if antes != depois:
        errors.append(f'idempotência quebrada no canônico: {antes} → {depois}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
