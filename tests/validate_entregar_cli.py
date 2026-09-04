#!/usr/bin/env python3
"""O entregar valida o contrato antes de gerar, simula por padrão, e diz quando
não consegue gerar PDF."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import entregaveis, padrao  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


CORPO = '\n'.join(f'## {i}. {nome}\n\nconteúdo da seção.\n'
                  for i, nome in enumerate(
                      entregaveis.CONTRATOS['ata']['secoes'], start=1))

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    corpo = raiz / '0-apoio' / 'corpo-ata.md'
    corpo.write_text(CORPO, encoding='utf-8')
    destino = raiz / padrao.destino('ata')

    seco = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
              '--corpo', str(corpo))
    if seco.returncode != 0:
        errors.append(f'entregar falhou: {seco.stdout}{seco.stderr}')
    if list(destino.glob('*.html')):
        errors.append('a simulação gravou o entregável')
    if 'cria' not in seco.stdout:
        errors.append('a simulação não mostrou o plano')

    ap = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
            '--corpo', str(corpo), '--apply')
    if ap.returncode != 0:
        errors.append(f'entregar --apply falhou: {ap.stdout}{ap.stderr}')
    gerados = list(destino.glob('*.html'))
    if not gerados:
        errors.append('--apply não gravou o HTML')
    else:
        html = gerados[0].read_text(encoding='utf-8')
        if '@font-face' not in html:
            errors.append('o entregável não é autocontido')
        if 'Identificação' not in html:
            errors.append('o corpo não entrou no documento')

    quebrado = raiz / '0-apoio' / 'corpo-quebrado.md'
    quebrado.write_text('## 1. Identificação\n', encoding='utf-8')
    r = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
           '--corpo', str(quebrado))
    if r.returncode == 0:
        errors.append('corpo fora do contrato deveria reprovar')
    if 'SECAO' not in r.stdout + r.stderr:
        errors.append('a reprovação não citou a regra violada')

    pdf = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
             '--corpo', str(corpo), '--pdf', '--apply')
    saida = pdf.stdout + pdf.stderr
    if not list(destino.glob('*.pdf')) and 'PDF' not in saida:
        errors.append('sem renderizador, a ausência do PDF precisa ser anunciada')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
