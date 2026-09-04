#!/usr/bin/env python3
"""O handoff só sai com o gate aberto, e leva a matriz dentro."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import padrao, registry  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'x'}, {'id': 'RN-002', 'enunciado': 'y'}])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'a', 'deriva_de': 'RN-001'}])

    r = dk('handoff', '--projeto', str(raiz))
    if r.returncode == 0:
        errors.append('gate com bloqueio deveria reprovar')
    if 'cobertura' not in r.stdout:
        errors.append('o gate não listou o item que bloqueou')
    if 'dk entender' not in r.stdout:
        errors.append('o bloqueio não deu o comando que resolve')
    if list((raiz / padrao.destino('handoff')).glob('handoff-*.html')):
        errors.append('gate fechado e mesmo assim gerou o pacote')
    if '[ ]' not in r.stdout or '[x]' not in r.stdout:
        errors.append('o gate não mostra o estado item a item')

    m = dk('handoff', '--projeto', str(raiz), '--matriz')
    if m.returncode != 0:
        errors.append('--matriz é só leitura e não deveria depender do gate')
    if 'REQ-001' not in m.stdout:
        errors.append('--matriz não emitiu a linha do requisito')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
