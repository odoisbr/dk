#!/usr/bin/env python3
"""Os seis tipos de inconsistência, portados do community.

O que é determinístico o código decide. O que exige leitura, ele marca como
candidato e declara que não decidiu."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import consistencia  # noqa: E402

errors = []

if len(consistencia.TIPOS) != 7:
    errors.append(f'esperados 7 tipos, há {len(consistencia.TIPOS)}')
for nome in ('CONFLITO', 'DUPLICATA', 'ORFAO', 'REFERENCIA-INDEFINIDA',
             'NF-SEM-CRITERIO', 'REGRA-CIRCULAR', 'TITULO-TRUNCADO'):
    if nome not in consistencia.TIPOS:
        errors.append(f'tipo {nome} ausente')

REGRAS = [
    {'id': 'RN-001', 'enunciado': 'o gestor revoga o convênio'},
    {'id': 'RN-002', 'enunciado': 'depende de RN-003 estar aprovada',
     'depende': ['RN-003']},
    {'id': 'RN-003', 'enunciado': 'depende de RN-002 estar aprovada',
     'depende': ['RN-002']},
]

REQUISITOS = [
    {'id': 'REQ-001', 'titulo': 'o gestor deve poder revogar o convênio',
     'deriva_de': 'RN-001'},
    {'id': 'REQ-002', 'titulo': 'o gestor deve poder revogar convênios',
     'deriva_de': 'RN-001'},
    {'id': 'REQ-003', 'titulo': 'sem âncora nenhuma', 'deriva_de': 'RN-404'},
    {'id': 'REQ-004', 'titulo': 'a interface deve ser rápida e intuitiva',
     'deriva_de': 'RN-001'},
    {'id': 'REQ-005', 'titulo': 'sincronizar com o Portal Transparência',
     'deriva_de': 'RN-001'},
]

achados = consistencia.analisar(REGRAS, REQUISITOS)
tipos = {a['tipo'] for a in achados}

for esperado in ('DUPLICATA', 'ORFAO', 'NF-SEM-CRITERIO', 'REGRA-CIRCULAR'):
    if esperado not in tipos:
        errors.append(f'{esperado} não foi detectado')

dup = [a for a in achados if a['tipo'] == 'DUPLICATA']
if dup and set(dup[0]['itens']) != {'REQ-001', 'REQ-002'}:
    errors.append(f"duplicata apontou o par errado: {dup[0]['itens']}")

orfao = [a for a in achados if a['tipo'] == 'ORFAO']
if orfao and orfao[0]['itens'] != ['REQ-003']:
    errors.append(f"órfão errado: {orfao[0]['itens']}")

nf = [a for a in achados if a['tipo'] == 'NF-SEM-CRITERIO']
if nf and nf[0]['itens'] != ['REQ-004']:
    errors.append(f"NF sem critério errado: {nf[0]['itens']}")

circ = [a for a in achados if a['tipo'] == 'REGRA-CIRCULAR']
if not circ:
    errors.append('ciclo não detectado')
elif set(circ[0]['itens']) != {'RN-002', 'RN-003'}:
    errors.append(f"ciclo errado: {circ[0]['itens']}")
if len(circ) > 1:
    errors.append(f'o mesmo ciclo foi relatado {len(circ)} vezes')

for a in achados:
    if not a.get('evidencia'):
        errors.append(f'achado sem evidência: {a}')
    if a.get('urgencia') not in ('BLOQUEIA-AVANCO', 'RESOLVE-ANTES-DO-DESIGN',
                                'PODE-POSTERGAR'):
        errors.append(f"urgência inválida em {a['tipo']}: {a.get('urgencia')}")
    if 'decidido_por' not in a:
        errors.append(f"{a['tipo']} não diz quem decidiu")

for a in [x for x in achados if x['tipo'] == 'CONFLITO']:
    if a['decidido_por'] != 'skill':
        errors.append('conflito semântico não pode ser decidido por código')


# Esquema canônico: a âncora é `sources`, não `deriva_de`. A versão anterior
# marcou os 86 requisitos de um projeto real como órfãos.
canonico = consistencia.analisar(
    [{'id': 'RN-001', 'title': 'validade por subcategoria', 'sources': ['SRC-001']}],
    [{'id': 'RF-001', 'title': 'o gestor altera a categoria do titular',
      'sources': ['SRC-015']}])
if 'ORFAO' in {a['tipo'] for a in canonico}:
    errors.append('requisito com fonte declarada não é órfão')

# Título truncado: comparar pelo rótulo cortado acusa duplicata que não existe.
truncados = [
    {'id': 'RF-024', 'title': 'O beneficiário (cat',
     'description': 'O beneficiário (cat. 40) deve poder incluir dependentes',
     'sources': ['SRC-001']},
    {'id': 'RF-025', 'title': 'O beneficiário (cat',
     'description': 'O beneficiário (cat. 40) deve poder remover dependentes',
     'sources': ['SRC-001']},
]
r = consistencia.analisar([], truncados)
tipos_t = {a['tipo'] for a in r}
if 'TITULO-TRUNCADO' not in tipos_t:
    errors.append('título cortado deveria ser detectado')
if 'DUPLICATA' in tipos_t:
    errors.append('a comparação usou o rótulo cortado e acusou duplicata falsa')

limpo = consistencia.analisar(
    [{'id': 'RN-001', 'enunciado': 'x'}],
    [{'id': 'REQ-001', 'titulo': 'resposta em até 2 segundos',
      'deriva_de': 'RN-001'}])
if limpo:
    errors.append(f'conjunto sadio não deveria ter achado: {limpo}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
