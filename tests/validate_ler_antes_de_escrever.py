#!/usr/bin/env python3
"""Nenhum artefato é gravado sem que sua fonte tenha sido lida na sessão.

É o invariante que fecha a dor nº 1: requisitos que já existem no projeto sendo
ignorados e sobrescritos, em vez de atualizados."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, leitura, ops  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    io.atomic_write(raiz / 'fonte.md', 'requisito existente')
    io.atomic_write(raiz / 'saida.md', 'versão antiga')

    reg = leitura.Registro()
    if reg.foi_lido(raiz / 'fonte.md'):
        errors.append('registro nasceu achando que já leu')

    op = ops.Operacao(raiz, escopo=['saida.md'], registro=reg,
                      fontes=[raiz / 'fonte.md'])
    try:
        op.planejar(raiz / 'saida.md', 'nova versão')
    except ops.FonteNaoLida:
        pass
    else:
        errors.append('escrita sem leitura prévia da fonte não foi recusada')

    conteudo = reg.ler(raiz / 'fonte.md')
    if conteudo != 'requisito existente':
        errors.append('ler() não devolveu o conteúdo do arquivo')
    if not reg.foi_lido(raiz / 'fonte.md'):
        errors.append('ler() não registrou a leitura')

    op2 = ops.Operacao(raiz, escopo=['saida.md'], registro=reg,
                       fontes=[raiz / 'fonte.md'])
    plano = op2.planejar(raiz / 'saida.md', 'nova versão')
    if plano['acao'] != 'modifica':
        errors.append('após a leitura, o plano deveria ser aceito')
    op2.aplicar()
    if (raiz / 'saida.md').read_text(encoding='utf-8') != 'nova versão':
        errors.append('aplicar() não gravou depois da leitura')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
