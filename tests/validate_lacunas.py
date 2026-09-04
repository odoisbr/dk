#!/usr/bin/env python3
"""Lacuna só existe com âncora no checklist, e vem com prioridade."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import lacunas, padrao, registry  # noqa: E402

errors = []

checklist = lacunas.carregar_checklist()
if len(checklist) < 5:
    errors.append(f'checklist com {len(checklist)} itens é curto demais')
for item in checklist:
    for campo in ('id', 'tema', 'pergunta', 'prioridade', 'sinais'):
        if campo not in item:
            errors.append(f'{item.get("id")}: sem campo {campo}')
    if item.get('prioridade') not in ('CRITICA', 'IMPORTANTE', 'DESEJAVEL'):
        errors.append(f'{item.get("id")}: prioridade inválida')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [])
    registry.gravar(raiz, 'requisitos', [])

    achados = lacunas.analisar(raiz)
    if len(achados) != len(checklist):
        errors.append(f'projeto vazio: {len(achados)} lacunas para '
                      f'{len(checklist)} itens de checklist')
    if any(a['status'] != 'AUSENTE' for a in achados):
        errors.append('projeto vazio deveria ter tudo AUSENTE')
    for a in achados:
        if not a.get('evidencia'):
            errors.append(f'lacuna sem evidência: {a}')
        if not a.get('id', '').startswith('L-'):
            errors.append(f'lacuna sem id no padrão L-XX: {a.get("id")}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001',
         'enunciado': 'o gestor com perfil de acesso revoga; permissão exigida'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001',
         'titulo': 'o objetivo é reduzir o indicador de convênios vencidos',
         'deriva_de': 'RN-001'},
    ])
    achados = lacunas.analisar(raiz)
    por_id = {a['item']: a for a in achados}
    if por_id.get('CL-01', {}).get('status') == 'AUSENTE':
        errors.append('CL-01 tem sinal de objetivo/indicador; não é AUSENTE')
    if por_id.get('CL-07', {}).get('status') == 'AUSENTE':
        errors.append('CL-07 tem sinal de permissão; não é AUSENTE')
    if por_id.get('CL-06', {}).get('status') != 'AUSENTE':
        errors.append(f"CL-06 deveria ser AUSENTE, veio "
                      f"{por_id.get('CL-06', {}).get('status')}")

    criticas = [a for a in achados if a['prioridade'] == 'CRITICA'
                and a['status'] == 'AUSENTE']
    if not criticas:
        errors.append('deveria restar ao menos uma lacuna crítica ausente')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
