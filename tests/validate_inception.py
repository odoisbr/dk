#!/usr/bin/env python3
"""Lean Inception: a agenda cobrada contra o registro que o projeto tem.

O formato do registro não foi inventado: `registry/lean-inception.json` existe no
design-credenciamento com `tipo`, `ordem`, `titulo`, `status`, `conteudo`,
`sources` — e é essa forma que o teste usa."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import inception  # noqa: E402

errors = []


def projeto(itens):
    d = Path(tempfile.mkdtemp()) / 'p'
    (d / 'registry').mkdir(parents=True)
    (d / 'registry' / 'lean-inception.json').write_text(
        json.dumps(itens, ensure_ascii=False), encoding='utf-8')
    return d


# ── a agenda é dado, não código ──
agenda = inception.agenda()
if [a['n'] for a in agenda['atividades']] != list(range(1, 12)):
    errors.append('a agenda das onze atividades não está completa nem em ordem')

# ── projeto sem registro nenhum não está "descoberto": está por começar ──
vazio = Path(tempfile.mkdtemp()) / 'p'
(vazio / 'registry').mkdir(parents=True)
r = inception.avaliar(vazio)
if r['estado'] != 'por-comecar':
    errors.append(f"projeto sem lean-inception.json deu {r['estado']}")
if r['cobertas'] or r['percentual']:
    errors.append('verdade vácua: agenda vazia contada como coberta')
if not any(a['id'] == 'INC-SEM-REGISTRO' for a in r['achados']):
    errors.append('a ausência do registro deveria ser dita, não silenciada')

# ── a forma real do design-credenciamento ──
REAIS = [
    {'id': 'LI-001', 'tipo': 'visao', 'ordem': 1, 'status': 'rascunho',
     'titulo': 'Portal assume os fluxos hoje presos ao SMA',
     'conteudo': 'O módulo responde pelo ciclo de vida das credenciais.',
     'sources': ['SRC-015']},
    {'id': 'LI-002', 'tipo': 'stakeholder', 'ordem': 1, 'status': 'rascunho',
     'titulo': 'GEREL', 'conteudo': 'Sesc/DF',
     'papel': 'Solicitante da demanda', 'sources': ['SRC-015']},
    {'id': 'LI-003', 'tipo': 'objetivo', 'ordem': 1, 'status': 'rascunho',
     'titulo': 'Autonomia da GEREL', 'conteudo': 'Reduzir dependência do SMA.',
     'sources': ['SRC-015']},
]
r = inception.avaliar(projeto(REAIS))
if r['estado'] == 'por-comecar':
    errors.append('projeto com três atividades não está por começar')
cobertas = {a['tipo'] for a in r['atividades']
            if a['estado'] == 'coberta' and a['n']}
if cobertas != {'visao', 'objetivo'}:
    errors.append(f'atividades cobertas erradas: {sorted(cobertas)}')
ausentes = [a for a in r['atividades'] if a['estado'] == 'ausente' and a['n']]
if len(ausentes) != 9:
    errors.append(f'nove atividades deveriam faltar, faltaram {len(ausentes)}')
if r['percentual'] != 18:
    errors.append(f"percentual errado: {r['percentual']}")

# stakeholder é complemento reconhecido, não item fora da agenda
if any(a['id'] == 'INC-FORA-DA-AGENDA' and 'stakeholder' in a['evidencia']
       for a in r['achados']):
    errors.append('stakeholder é complemento reconhecido, não item estranho')

# ── item sem âncora em fonte ──
r = inception.avaliar(projeto([
    {'id': 'LI-001', 'tipo': 'visao', 'titulo': 'Visão', 'conteudo': 'texto',
     'sources': []}]))
if not any(a['id'] == 'INC-SEM-FONTE' for a in r['achados']):
    errors.append('visão sem fonte deveria ser apontada')

# ── canvas MVP incompleto: os seis campos são o contrato ──
r = inception.avaliar(projeto([
    {'id': 'LI-009', 'tipo': 'canvas-mvp', 'titulo': 'MVP', 'conteudo': 'x',
     'proposta': 'a', 'segmento': 'b', 'sources': ['SRC-001']}]))
falta = [a for a in r['achados'] if a['id'] == 'INC-CAMPO']
if not falta:
    errors.append('canvas sem resultado, métrica, custo e risco deveria reprovar')
elif 'metrica' not in falta[0]['evidencia']:
    errors.append(f"o campo faltante não foi nomeado: {falta[0]['evidencia']}")
if [a for a in r['atividades'] if a['tipo'] == 'canvas-mvp'][0]['estado'] == 'coberta':
    errors.append('atividade com campo faltando não está coberta')

# ── tipo que não é da agenda nem complemento ──
r = inception.avaliar(projeto([
    {'id': 'LI-001', 'tipo': 'almoco', 'titulo': 'x', 'conteudo': 'y',
     'sources': ['SRC-001']}]))
fora = [a for a in r['achados'] if a['id'] == 'INC-FORA-DA-AGENDA']
if not fora:
    errors.append('tipo estranho deveria ser apontado')
elif fora[0]['impacto'] == 'alto':
    errors.append('tipo estranho avisa, não bloqueia: o registro é do projeto')

# ── toda conclusão declara quem decidiu ──
for a in inception.avaliar(projeto(REAIS))['achados']:
    if a.get('decidido_por') not in ('codigo', 'skill'):
        errors.append(f"{a['id']} não declara decidido_por")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
