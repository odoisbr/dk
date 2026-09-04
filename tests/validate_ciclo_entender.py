#!/usr/bin/env python3
"""O furo é detectado: regra sem requisito, requisito sem entregável,
lacuna crítica em aberto.

É o outro lado do teste da espinha. Aquele prova que o requisito não duplica;
este prova que o que falta aparece."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import padrao, registry  # noqa: E402

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

    # o furo: uma regra é acrescentada sem requisito derivado
    regras = registry.carregar(projeto, 'regras')
    regras.append({'id': 'RN-099',
                   'enunciado': 'convênio revogado não pode ser reativado',
                   'fonte': 'ata 14/08', 'citacao': 'não pode voltar'})
    registry.gravar(projeto, 'regras', regras)

    saida = dk('entender', '--projeto', str(projeto), '--json')
    if saida.returncode != 0:
        errors.append(f'entender falhou: {saida.stdout}{saida.stderr}')
    dados = json.loads(saida.stdout)

    if 'RN-099' not in dados['cobertura']['regras_sem_requisito']:
        errors.append('o furo não foi detectado: RN-099 tem requisito?')

    if not dados['cobertura']['requisitos_sem_entregavel']:
        errors.append('sem entregável gerado, os requisitos deveriam aparecer '
                      'como fora do entregável')

    criticas = [a for a in dados['lacunas']
                if a['prioridade'] == 'CRITICA' and a['status'] == 'AUSENTE']
    if not criticas:
        errors.append('uma reunião de três falas não cobre o checklist inteiro; '
                      'deveria haver lacuna crítica')

    for a in dados['consistencia']:
        if a['decidido_por'] not in ('codigo', 'skill'):
            errors.append(f'achado sem dono de decisão: {a}')

    # o relatório em texto precisa dizer o número, não só listar
    texto = dk('entender', '--projeto', str(projeto))
    if 'lacuna(s) crítica(s)' not in texto.stdout:
        errors.append('o relatório não fecha com a contagem de críticas')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
