#!/usr/bin/env python3
"""Verificação do pacote, sem runner externo.

Roda todo `tests/validate_*.py` como processo próprio e agrega o resultado.
Um validador novo entra por glob — não há lista para esquecer de atualizar."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def main() -> int:
    falhas = []
    # `Path.glob` em vez de `glob.glob(root_dir=)`: root_dir só existe no 3.10,
    # e o piso do pacote é 3.9.
    for teste in sorted(str(p.relative_to(RAIZ))
                        for p in RAIZ.glob('tests/validate_*.py')):
        r = subprocess.run([sys.executable, teste], cwd=str(RAIZ),
                           capture_output=True, text=True)
        marca = 'ok  ' if r.returncode == 0 else 'FALHA'
        print(f'{marca} {teste}')
        if r.returncode != 0:
            falhas.append(teste)
            saida = (r.stdout + r.stderr).strip()
            if saida:
                print('      ' + saida.replace('\n', '\n      '))
    print()
    print(f'{len(falhas)} falha(s)' if falhas else 'tudo verde')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
