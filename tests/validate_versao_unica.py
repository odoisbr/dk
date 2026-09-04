#!/usr/bin/env python3
"""A versão é declarada em um lugar só. Toda outra ocorrência é derivada."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import versao  # noqa: E402

errors = []

canonica = versao.versao_canonica()
if not canonica:
    errors.append('versao_canonica() vazia')

for caminho, declarada in versao.fontes().items():
    if declarada != canonica:
        errors.append(f'{caminho} declara {declarada}, canônica é {canonica}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
