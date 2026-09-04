#!/usr/bin/env python3
"""Toda escrita simula antes de aplicar, e só toca o que foi declarado.

Cobre a dor relatada no protótipo: pede-se um ajuste e a ferramenta altera
arquivo que ninguém pediu, quebrando o que já estava pronto."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, ops  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    io.atomic_write(raiz / 'dentro.txt', 'antes')
    io.atomic_write(raiz / 'fora.txt', 'intocado')

    op = ops.Operacao(raiz, escopo=['dentro.txt'])
    plano = op.planejar(raiz / 'dentro.txt', 'depois')

    if plano['acao'] != 'modifica':
        errors.append(f"acao esperada 'modifica', veio {plano['acao']!r}")
    if 'antes' not in plano['diff'] or 'depois' not in plano['diff']:
        errors.append('o plano não mostra o diff do que muda')
    if (raiz / 'dentro.txt').read_text(encoding='utf-8') != 'antes':
        errors.append('planejar() escreveu em disco — simulação deve ser inerte')

    escritos = op.aplicar()
    if (raiz / 'dentro.txt').read_text(encoding='utf-8') != 'depois':
        errors.append('aplicar() não gravou')
    if escritos != [raiz / 'dentro.txt']:
        errors.append(f'aplicar() devolveu {escritos}')

    op2 = ops.Operacao(raiz, escopo=['dentro.txt'])
    try:
        op2.planejar(raiz / 'fora.txt', 'invadido')
    except ops.ForaDoEscopo:
        pass
    else:
        errors.append('escrita fora do escopo declarado não foi recusada')

    if (raiz / 'fora.txt').read_text(encoding='utf-8') != 'intocado':
        errors.append('arquivo fora do escopo foi alterado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
