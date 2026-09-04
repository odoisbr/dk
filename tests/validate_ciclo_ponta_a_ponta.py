#!/usr/bin/env python3
"""O ciclo inteiro: insumo de reunião → regras → requisitos, com as quatro asserções.

A quarta é a que importa mais: insumo alterado ATUALIZA o requisito existente em
vez de criar um novo ao lado. É o teste de regressão do furo relatado pelo time."""
from __future__ import annotations
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import registry  # noqa: E402

FIXTURE = RAIZ / 'tests' / 'fixtures' / 'projeto-exemplo'
errors = []


def rodar(projeto: Path, insumo: Path):
    return subprocess.run(
        [sys.executable, str(RAIZ / 'bin' / 'dk'), 'levantar',
         '--projeto', str(projeto), '--insumo', str(insumo), '--apply'],
        capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    shutil.copytree(FIXTURE, projeto)
    primeiro = projeto / '0-apoio' / 'reunioes' / '2026-08-14-convenios.md'

    # simulação não grava
    seco = subprocess.run(
        [sys.executable, str(RAIZ / 'bin' / 'dk'), 'levantar',
         '--projeto', str(projeto), '--insumo', str(primeiro)],
        capture_output=True, text=True)
    if seco.returncode != 0:
        errors.append(f'simulação falhou: {seco.stdout}{seco.stderr}')
    if (projeto / 'registry' / 'requisitos.json').exists():
        errors.append('a simulação gravou em disco')

    # asserção 1: o artefato foi gerado
    r1 = rodar(projeto, primeiro)
    if r1.returncode != 0:
        errors.append(f'primeira execução falhou: {r1.stdout}{r1.stderr}')
    if not (projeto / 'registry' / 'requisitos.json').exists():
        errors.append('asserção 1: requisitos.json não foi gerado')

    # asserção 2: o registro foi atualizado, não só o arquivo
    regras_1 = registry.carregar(projeto, 'regras')
    req_1 = registry.carregar(projeto, 'requisitos')
    if not regras_1:
        errors.append('asserção 2: nenhuma regra no registro')
    if not req_1:
        errors.append('asserção 2: nenhum requisito no registro')
    for q in req_1:
        if not q.get('deriva_de'):
            errors.append(f"asserção 2: {q.get('id')} sem vínculo com a regra")

    # asserção 3: rodar de novo com o mesmo insumo não duplica
    r2 = rodar(projeto, primeiro)
    if r2.returncode != 0:
        errors.append(f'segunda execução falhou: {r2.stdout}{r2.stderr}')
    req_2 = registry.carregar(projeto, 'requisitos')
    if len(req_2) != len(req_1):
        errors.append(
            f'asserção 3: idempotência quebrada — {len(req_1)} → {len(req_2)} requisitos')
    if registry.carregar(projeto, 'regras') != regras_1:
        errors.append('asserção 3: o registro de regras mudou sem insumo novo')

    # asserção 4: insumo alterado ATUALIZA o existente, não cria ao lado
    revisao = projeto / '2026-08-28-convenios-revisao.md'
    r3 = rodar(projeto, revisao)
    if r3.returncode != 0:
        errors.append(f'terceira execução falhou: {r3.stdout}{r3.stderr}')
    req_3 = registry.carregar(projeto, 'requisitos')
    if len(req_3) != len(req_1):
        errors.append(
            f'asserção 4: o insumo revisado criou requisito ao lado — '
            f'{len(req_1)} → {len(req_3)}. É exatamente o furo que o DK existe para impedir.')
    alvo = [q for q in req_3 if q['id'] == req_1[0]['id']]
    if not alvo:
        errors.append('asserção 4: o requisito original sumiu')
    elif 'motivo da revogação' not in alvo[0]['titulo']:
        errors.append(
            f"asserção 4: o requisito não foi atualizado com o texto novo: "
            f"{alvo[0]['titulo']!r}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
