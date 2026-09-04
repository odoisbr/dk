#!/usr/bin/env python3
"""O portão de release: nada é publicado com um item aberto.

O primeiro item é o que impede repetir o erro de origem do Kit anterior —
publicar sem o ciclo provado ponta a ponta."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

ITENS = [
    ('teste E2E da espinha verde', 'tests/validate_ciclo_ponta_a_ponta.py'),
    ('hooks ativos e verificados', 'tests/validate_hooks_ativos.py'),
    ('escrita atômica', 'tests/validate_escrita_atomica.py'),
    ('dry-run e escopo declarado', 'tests/validate_dry_run_e_escopo.py'),
    ('ler antes de escrever', 'tests/validate_ler_antes_de_escrever.py'),
    ('versão em fonte única', 'tests/validate_versao_unica.py'),
    ('portão e orçamento de catálogo', 'tests/validate_portao_e_orcamento.py'),
    ('enumeração por agente', 'tests/validate_enumeracao.py'),
    ('contrato de resposta', 'tests/validate_contrato_de_resposta.py'),
    ('llms.txt e llms-full.txt', 'tests/validate_contrato_llm.py'),
    ('governança recuperada', 'tests/validate_governanca.py'),
    ('dogfooding: o dk audita o próprio dk', 'tests/validate_dogfooding.py'),
    ('varredura sem leitura e sem segredo', 'tests/validate_scan.py'),
    ('ciclo do entregável', 'tests/validate_ciclo_entregavel.py'),
    ('contrato dos entregáveis', 'tests/validate_entregaveis.py'),
    ('padrão de projeto', 'tests/validate_padrao.py'),
    ('tokens da marca', 'tests/validate_marca.py'),
    ('o furo aparece (ciclo entender)', 'tests/validate_ciclo_entender.py'),
    ('seis tipos de inconsistência', 'tests/validate_consistencia.py'),
    ('lacunas contra checklist', 'tests/validate_lacunas.py'),
    ('matriz de cobertura', 'tests/validate_cobertura.py'),
]

errors = []
for rotulo, teste in ITENS:
    caminho = RAIZ / teste
    if not caminho.exists():
        errors.append(f'[ ] {rotulo} — {teste} não existe')
        continue
    r = subprocess.run([sys.executable, str(caminho)], cwd=str(RAIZ),
                       capture_output=True, text=True)
    marca = '[x]' if r.returncode == 0 else '[ ]'
    print(f'{marca} {rotulo}')
    if r.returncode != 0:
        errors.append(f'{rotulo}: {teste} reprovou')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
