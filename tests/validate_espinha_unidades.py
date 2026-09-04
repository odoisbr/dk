#!/usr/bin/env python3
"""As unidades determinísticas da espinha, isoladas."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import espinha  # noqa: E402

errors = []

BRUTO = """Reunião 14/08 — Convênios
Fulana (gestora): o convênio não expira sozinho, quem tira do ar é o gestor.
Beltrano: e quando o prazo vence?
Fulana: fica vencido na lista, mas continua no ar até alguém revogar.
"""

a = espinha.ata(BRUTO)
if not a.get('data'):
    errors.append('ata sem data extraída')
if not a.get('participantes'):
    errors.append('ata sem participantes extraídos')
if 'Fulana' not in a.get('participantes', []):
    errors.append(f"participantes não incluem Fulana: {a.get('participantes')}")
if not a.get('falas'):
    errors.append('ata sem falas')

rs = espinha.regras(a, origem='0-apoio/reunioes/2026-08-14-convenios.md')
if not rs:
    errors.append('nenhuma regra candidata extraída da ata')
for r in rs:
    # O id não sai daqui: quem atribui é a gravação, consultando o contador do
    # projeto. Gerar id posicional colidia com o que o projeto real já tinha.
    if r.get('id'):
        errors.append(f'a espinha não deve atribuir id: {r["id"]!r}')
    if not r.get('origem_chave', '').startswith('0-apoio/reunioes/'):
        errors.append(f'regra sem âncora no insumo: {r.get("origem_chave")!r}')
    if not r.get('citacao'):
        errors.append(f'{r.get("origem_chave")}: regra sem citação de origem')

# A mesma origem gera a mesma chave; origem diferente gera chave diferente.
if [r['origem_chave'] for r in espinha.regras(a, origem='x.md')] == \
   [r['origem_chave'] for r in rs]:
    errors.append('insumos diferentes deveriam gerar chaves diferentes')

reqs = espinha.requisitos(rs)
for q in reqs:
    if q.get('id'):
        errors.append(f'a espinha não deve atribuir id ao requisito: {q["id"]!r}')
    if not q.get('origem_chave'):
        errors.append('requisito sem âncora de origem')

for i, r in enumerate(rs, 1):
    r['id'] = f'RN-{i:03d}'
for i, q in enumerate(reqs, 1):
    q['id'] = f'REQ-{i:03d}'
    q['deriva_de'] = rs[i - 1]['id']

cob = espinha.cobertura(reqs, rs)
if cob['regras_sem_requisito']:
    errors.append(f"regras sem requisito: {cob['regras_sem_requisito']}")
if cob['total_regras'] != len(rs):
    errors.append('cobertura contou regras errado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
