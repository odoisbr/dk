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

rs = espinha.regras(a)
if not rs:
    errors.append('nenhuma regra candidata extraída da ata')
for r in rs:
    if not r.get('id', '').startswith('RN-'):
        errors.append(f'regra sem id no padrão RN-: {r.get("id")!r}')
    if not r.get('citacao'):
        errors.append(f'{r.get("id")}: regra sem citação de origem')

reqs = espinha.requisitos(rs)
for q in reqs:
    if not q.get('id', '').startswith('REQ-'):
        errors.append(f'requisito sem id no padrão REQ-: {q.get("id")!r}')
    if not q.get('deriva_de'):
        errors.append(f'{q.get("id")}: requisito sem vínculo com a regra de origem')

cob = espinha.cobertura(reqs, rs)
if cob['regras_sem_requisito']:
    errors.append(f"regras sem requisito: {cob['regras_sem_requisito']}")
if cob['total_regras'] != len(rs):
    errors.append('cobertura contou regras errado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
