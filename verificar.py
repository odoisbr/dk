#!/usr/bin/env python3
"""Verificação do pacote, sem runner externo.

Roda todo `tests/validate_*.py` como processo próprio e agrega o resultado.
Um validador novo entra por glob — não há lista para esquecer de atualizar."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


# O portão de release é meta-teste: ele roda os outros. Fica fora da bateria
# normal para não duplicar a execução inteira a cada push.
META = {'tests/validate_release_gate.py'}


def main() -> int:
    falhas = []
    # `Path.glob` em vez de `glob.glob(root_dir=)`: root_dir só existe no 3.10,
    # e o piso do pacote é 3.9.
    for teste in sorted(str(p.relative_to(RAIZ))
                        for p in RAIZ.glob('tests/validate_*.py')):
        if teste in META:
            continue
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

    if '--release' in sys.argv:
        print()
        r = subprocess.run([sys.executable, 'tests/validate_release_gate.py'],
                           cwd=str(RAIZ), capture_output=True, text=True)
        print((r.stdout + r.stderr).strip())
        if r.returncode != 0 or falhas:
            print('portão de release fechado — publicação bloqueada')
            return 1
        print('portão de release aberto')

    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
