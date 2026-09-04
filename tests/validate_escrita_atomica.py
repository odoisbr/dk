#!/usr/bin/env python3
"""Escrita interrompida não corrompe o arquivo que já existia.

O modo `open(..., 'w')` trunca antes de escrever: se o processo morre no meio,
o arquivo fica pela metade. Dois scripts do Kit anterior ainda faziam isso
(achado DK-109)."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    alvo = Path(d) / 'sub' / 'arquivo.txt'

    io.atomic_write(alvo, 'primeiro')
    if alvo.read_text(encoding='utf-8') != 'primeiro':
        errors.append('atomic_write não gravou o conteúdo inicial')

    class Explode(str):
        def encode(self, *a, **k):
            raise RuntimeError('falha simulada no meio da escrita')

    try:
        io.atomic_write(alvo, Explode('segundo'))
    except RuntimeError:
        pass
    else:
        errors.append('a falha simulada não propagou')

    if alvo.read_text(encoding='utf-8') != 'primeiro':
        errors.append('o conteúdo anterior foi corrompido por escrita interrompida')

    sobras = [p.name for p in alvo.parent.iterdir() if p.name != 'arquivo.txt']
    if sobras:
        errors.append(f'arquivo temporário não removido: {sobras}')

    j = Path(d) / 'dados.json'
    io.atomic_json(j, {'a': 1, 'acento': 'ação'})
    if json.loads(j.read_text(encoding='utf-8')) != {'a': 1, 'acento': 'ação'}:
        errors.append('atomic_json não preservou o conteúdo')
    if 'ação' not in j.read_text(encoding='utf-8'):
        errors.append('atomic_json escapou caractere acentuado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
